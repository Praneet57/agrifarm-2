from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.demand import Demand
from app.models.demand_notification import DemandSmsNotification
from app.models.user import User
from app.routers.sms import verify_twilio_signature
from app.schemas import DemandPublicOut
from app.services.demand_alert_service import (
    build_demand_alert_template_variables,
    find_nearby_recipients,
    haversine_distance_km,
    normalize_indian_mobile,
    record_sms_failure,
)
from app.services.notification_service import (
    SmsDeliveryError,
    SmsProviderNotConfigured,
    send_demand_alert_sms,
)

def _phone() -> str:
    return f"9{uuid4().int % 10**9:09d}"


def test_haversine_distance_filters_at_ten_km():
    assert haversine_distance_km(13.0, 80.0, 13.0, 80.0) == 0
    assert haversine_distance_km(0.0, 0.0, 0.0, 0.0899) < 10
    assert haversine_distance_km(0.0, 0.0, 0.0, 0.091) > 10


def test_indian_mobile_normalization_for_provider():
    assert normalize_indian_mobile("9876543210") == "+919876543210"
    assert normalize_indian_mobile("+91 98765-43210") == "+919876543210"
    assert normalize_indian_mobile("12345") is None


@pytest.mark.asyncio
async def test_nearby_selection_requires_consent_verification_and_range(db, monkeypatch):
    monkeypatch.setattr(settings, "SMS_ALERT_RECIPIENT_ROLE", "all")
    suffix = uuid4().hex[:8]
    candidates = [
        User(
            full_name=f"Eligible {suffix}",
            phone=_phone(),
            hashed_password="test",
            role="farmer",
            is_active=True,
            is_verified=True,
            sms_alerts_opt_in=True,
            share_location_for_alerts=True,
            latitude=13.08,
            longitude=80.0,
        ),
        User(
            full_name=f"Eligible buyer {suffix}",
            phone=_phone(),
            hashed_password="test",
            role="buyer",
            is_active=True,
            is_verified=True,
            sms_alerts_opt_in=True,
            share_location_for_alerts=True,
            latitude=13.01,
            longitude=80.0,
        ),
        User(
            full_name=f"Too far {suffix}",
            phone=_phone(),
            hashed_password="test",
            role="farmer",
            is_active=True,
            is_verified=True,
            sms_alerts_opt_in=True,
            share_location_for_alerts=True,
            latitude=13.11,
            longitude=80.0,
        ),
        User(
            full_name=f"No consent {suffix}",
            phone=_phone(),
            hashed_password="test",
            role="buyer",
            is_active=True,
            is_verified=True,
            sms_alerts_opt_in=False,
            share_location_for_alerts=True,
            latitude=13.01,
            longitude=80.0,
        ),
        User(
            full_name=f"Unverified {suffix}",
            phone=_phone(),
            hashed_password="test",
            role="farmer",
            is_active=True,
            is_verified=False,
            sms_alerts_opt_in=True,
            share_location_for_alerts=True,
            latitude=13.01,
            longitude=80.0,
        ),
    ]
    db.add_all(candidates)
    await db.flush()

    selected = await find_nearby_recipients(
        db, 13.0, 80.0, exclude_user_id=-1
    )
    selected_ids = {user.id for user in selected}
    assert candidates[0].id in selected_ids
    assert candidates[1].id in selected_ids
    assert candidates[2].id not in selected_ids
    assert candidates[3].id not in selected_ids
    assert candidates[4].id not in selected_ids

    monkeypatch.setattr(settings, "SMS_ALERT_RECIPIENT_ROLE", "farmer")
    farmer_only = await find_nearby_recipients(
        db, 13.0, 80.0, exclude_user_id=-1
    )
    farmer_only_ids = {user.id for user in farmer_only}
    assert candidates[0].id in farmer_only_ids
    assert candidates[1].id not in farmer_only_ids
    buyer_only = await find_nearby_recipients(
        db, 13.0, 80.0, exclude_user_id=-1, recipient_role="buyer"
    )
    buyer_only_ids = {user.id for user in buyer_only}
    assert candidates[1].id in buyer_only_ids
    assert candidates[0].id not in buyer_only_ids


@pytest.mark.asyncio
async def test_unique_demand_recipient_prevents_duplicate_notification(db):
    buyer = User(
        full_name="Demand Buyer",
        phone=_phone(),
        hashed_password="test",
        role="buyer",
    )
    recipient = User(
        full_name="Alert Recipient",
        phone=_phone(),
        hashed_password="test",
        role="farmer",
    )
    db.add_all([buyer, recipient])
    await db.flush()
    demand = Demand(
        buyer_id=buyer.id,
        product_name="Tomatoes",
        category="Vegetables",
        quantity_kg=10,
        max_price_per_kg=20,
        district="Chennai",
    )
    db.add(demand)
    await db.flush()
    db.add_all([
        DemandSmsNotification(demand_id=demand.id, recipient_id=recipient.id),
        DemandSmsNotification(demand_id=demand.id, recipient_id=recipient.id),
    ])
    with pytest.raises(IntegrityError):
        await db.flush()
    await db.rollback()



def test_sms_failure_records_retry_or_unknown_delivery(monkeypatch):
    monkeypatch.setattr(settings, "SMS_ALERT_MAX_ATTEMPTS", 3)
    retryable = DemandSmsNotification(attempt_count=1)
    record_sms_failure(
        retryable,
        SmsDeliveryError("Provider throttled request", retryable=True),
    )
    assert retryable.status == "failed"
    assert retryable.next_attempt_at > datetime.now(timezone.utc)

    ambiguous = DemandSmsNotification(attempt_count=1)
    record_sms_failure(
        ambiguous,
        SmsDeliveryError(
            "Provider timed out",
            retryable=False,
            outcome_unknown=True,
        ),
    )
    assert ambiguous.status == "unknown"
    assert ambiguous.next_attempt_at is None


@pytest.mark.asyncio
async def test_alert_sms_never_falls_back_to_demo_when_unconfigured(monkeypatch):
    monkeypatch.setattr(settings, "TWILIO_ACCOUNT_SID", "")
    with pytest.raises(SmsProviderNotConfigured):
        await send_demand_alert_sms("+919999999999", {"1": "Tomatoes"})



def test_public_alert_template_uses_only_general_area_and_safe_link(monkeypatch):
    monkeypatch.setattr(settings, "APP_PUBLIC_URL", "https://market.example/")
    demand = Demand(
        id=42,
        product_name="Tomatoes",
        quantity_kg=25,
        district="Coimbatore",
    )
    variables = build_demand_alert_template_variables(demand)
    assert variables == {
        "1": "Tomatoes",
        "2": "25 kg",
        "3": "Urgent",
        "4": "Coimbatore",
        "5": "https://market.example/demand.html?id=42",
    }
    assert not {"buyer_id", "delivery_address", "latitude", "longitude"}.intersection(
        DemandPublicOut.model_fields
    )



def test_twilio_status_signature_rejects_tampered_callback():
    import base64
    import hashlib
    import hmac

    callback_url = "https://market.example/api/v1/sms/twilio/status"
    form_items = [("MessageSid", "SM123"), ("MessageStatus", "delivered")]
    token = "test-token"
    signed_data = callback_url + "".join(
        key + value for key, value in sorted(form_items)
    )
    signature = base64.b64encode(
        hmac.new(token.encode(), signed_data.encode(), hashlib.sha1).digest()
    ).decode()
    assert verify_twilio_signature(callback_url, form_items, signature, token)
    assert not verify_twilio_signature(
        callback_url, form_items, signature, "wrong-token"
    )
