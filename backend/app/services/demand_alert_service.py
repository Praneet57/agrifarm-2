import math
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.demand import Demand
from app.models.demand_notification import DemandSmsNotification
from app.models.product import Product
from app.models.user import User
from app.services.notification_service import SmsDeliveryError

EARTH_RADIUS_KM = 6371.0088
ALERT_RADIUS_KM = 10.0
DISPATCH_RECLAIM_SECONDS = 120


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = math.radians(lon2 - lon1)
    hav = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(min(1.0, max(0.0, hav))))


def normalize_indian_mobile(phone: str) -> Optional[str]:
    digits = re.sub(r"\D", "", phone)
    if re.fullmatch(r"[6-9]\d{9}", digits):
        return f"+91{digits}"
    if re.fullmatch(r"91[6-9]\d{9}", digits):
        return f"+{digits}"
    return None


async def find_nearby_recipients(
    db: AsyncSession,
    latitude: float,
    longitude: float,
    *,
    exclude_user_id: int,
    recipient_role: Optional[str] = None,
) -> list[User]:
    lat_delta = ALERT_RADIUS_KM / 110.574
    min_lat = max(-90.0, latitude - lat_delta)
    max_lat = min(90.0, latitude + lat_delta)
    cos_latitude = abs(math.cos(math.radians(latitude)))
    lon_delta = 180.0 if cos_latitude < 1e-8 else min(
        180.0, ALERT_RADIUS_KM / (111.320 * cos_latitude)
    )

    predicates = [
        User.is_active.is_(True),
        User.is_verified.is_(True),
        User.sms_alerts_opt_in.is_(True),
        User.share_location_for_alerts.is_(True),
        User.latitude.is_not(None),
        User.longitude.is_not(None),
        User.id != exclude_user_id,
        User.role == recipient_role if recipient_role else (
            User.role.in_(("farmer", "buyer"))
            if settings.SMS_ALERT_RECIPIENT_ROLE == "all"
            else User.role == settings.SMS_ALERT_RECIPIENT_ROLE
        ),
        User.latitude.between(min_lat, max_lat),
    ]

    if lon_delta < 180.0:
        min_lon, max_lon = longitude - lon_delta, longitude + lon_delta
        if min_lon < -180.0:
            predicates.append(or_(User.longitude >= min_lon + 360.0, User.longitude <= max_lon))
        elif max_lon > 180.0:
            predicates.append(or_(User.longitude >= min_lon, User.longitude <= max_lon - 360.0))
        else:
            predicates.append(User.longitude.between(min_lon, max_lon))

    lat1 = math.radians(latitude)
    lat2 = func.radians(User.latitude)
    delta_lat = lat2 - lat1
    delta_lon = func.radians(User.longitude - longitude)
    haversine_a = (
        func.pow(func.sin(delta_lat / 2.0), 2)
        + math.cos(lat1)
        * func.cos(lat2)
        * func.pow(func.sin(delta_lon / 2.0), 2)
    )
    distance_km = 2 * EARTH_RADIUS_KM * func.asin(func.sqrt(func.least(1.0, haversine_a)))
    query = select(User).where(and_(*predicates, distance_km <= ALERT_RADIUS_KM))
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_demand_notifications(
    db: AsyncSession, demand: Demand
) -> list[DemandSmsNotification]:
    if (
        not demand.is_urgent
        or not demand.allow_location_based_alerts
        or demand.latitude is None
        or demand.longitude is None
    ):
        return []

    recipients = await find_nearby_recipients(
        db, demand.latitude, demand.longitude, exclude_user_id=demand.buyer_id
    )
    notifications = [
        DemandSmsNotification(demand_id=demand.id, recipient_id=user.id)
        for user in recipients
    ]
    db.add_all(notifications)
    if notifications:
        await db.flush()
    return notifications

async def create_product_notifications(
    db: AsyncSession, product: Product
) -> list[DemandSmsNotification]:
    predicates = [
        User.is_active.is_(True),
        User.is_verified.is_(True),
        User.sms_alerts_opt_in.is_(True),
        User.id != product.farmer_id,
        User.role.in_(("farmer", "buyer")),
    ]
    # If the product has coordinates, only alert users within 10 km who share
    # their location; otherwise fall back to a system-wide broadcast.
    if product.latitude is not None and product.longitude is not None:
        predicates.append(User.share_location_for_alerts.is_(True))
        predicates.append(User.latitude.is_not(None))
        predicates.append(User.longitude.is_not(None))
        lat_delta = ALERT_RADIUS_KM / 110.574
        min_lat = max(-90.0, product.latitude - lat_delta)
        max_lat = min(90.0, product.latitude + lat_delta)
        cos_lat = abs(math.cos(math.radians(product.latitude)))
        lon_delta = 180.0 if cos_lat < 1e-8 else min(
            180.0, ALERT_RADIUS_KM / (111.320 * cos_lat)
        )
        predicates.append(User.latitude.between(min_lat, max_lat))
        if lon_delta < 180.0:
            min_lon = product.longitude - lon_delta
            max_lon = product.longitude + lon_delta
            if min_lon < -180.0:
                predicates.append(
                    or_(User.longitude >= min_lon + 360.0, User.longitude <= max_lon)
                )
            elif max_lon > 180.0:
                predicates.append(
                    or_(User.longitude >= min_lon, User.longitude <= max_lon - 360.0)
                )
            else:
                predicates.append(User.longitude.between(min_lon, max_lon))
        lat1 = math.radians(product.latitude)
        lat2 = func.radians(User.latitude)
        delta_lat = lat2 - lat1
        delta_lon = func.radians(User.longitude - product.longitude)
        haversine_a = (
            func.pow(func.sin(delta_lat / 2.0), 2)
            + math.cos(lat1)
            * func.cos(lat2)
            * func.pow(func.sin(delta_lon / 2.0), 2)
        )
        distance_km = (
            2 * EARTH_RADIUS_KM * func.asin(func.sqrt(func.least(1.0, haversine_a)))
        )
        result = await db.execute(
            select(User).where(and_(*predicates, distance_km <= ALERT_RADIUS_KM))
        )
    else:
        result = await db.execute(select(User).where(and_(*predicates)))
    recipients = list(result.scalars().all())
    notifications = [
        DemandSmsNotification(product_id=product.id, recipient_id=user.id)
        for user in recipients
    ]
    db.add_all(notifications)
    if notifications:
        await db.flush()
    return notifications


async def claim_notifications_for_dispatch(
    db: AsyncSession, *, batch_size: int = 100
) -> list[int]:
    now = datetime.now(timezone.utc)
    reclaim_before = now - timedelta(seconds=DISPATCH_RECLAIM_SECONDS)
    await db.execute(
        update(DemandSmsNotification)
        .where(
            DemandSmsNotification.status == "sending",
            DemandSmsNotification.last_attempt_at <= reclaim_before,
        )
        .values(
            status="unknown",
            failure_reason="Worker stopped while delivery outcome was unknown",
        )
    )
    result = await db.execute(
        select(DemandSmsNotification)
        .where(
            or_(
                and_(
                    DemandSmsNotification.status == "queued",
                    or_(
                        DemandSmsNotification.dispatch_claimed_at.is_(None),
                        DemandSmsNotification.dispatch_claimed_at <= reclaim_before,
                    ),
                ),
                and_(
                    DemandSmsNotification.status == "failed",
                    DemandSmsNotification.next_attempt_at.is_not(None),
                    DemandSmsNotification.next_attempt_at <= now,
                    or_(
                        DemandSmsNotification.dispatch_claimed_at.is_(None),
                        DemandSmsNotification.dispatch_claimed_at <= reclaim_before,
                    ),
                ),
            ),
            DemandSmsNotification.attempt_count < settings.SMS_ALERT_MAX_ATTEMPTS,
        )
        .order_by(DemandSmsNotification.created_at)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )
    notifications = list(result.scalars().all())
    for notification in notifications:
        notification.status = "queued"
        notification.dispatch_claimed_at = now
    await db.commit()
    return [notification.id for notification in notifications]


def build_alert_template_variables(item, item_type: str) -> Optional[dict[str, str]]:
    base_url = settings.APP_PUBLIC_URL.strip().rstrip("/")
    parsed_base_url = urlparse(base_url)
    # In DEBUG mode allow http:// so local testing works without HTTPS
    if not parsed_base_url.netloc:
        return None
    if not settings.DEBUG and parsed_base_url.scheme != "https":
        return None
    if item_type == "demand":
        name = item.product_name
        quantity = item.quantity_kg
        urgency = "Urgent"
        area = item.district or "Nearby area"
        view_url = f"{base_url}/demand.html?id={item.id}"
    elif item_type == "product":
        name = item.name
        quantity = item.quantity_kg
        urgency = "New listing"
        area = item.district or "Area not provided"
        view_url = f"{base_url}/workspace.html?view_product={item.id}"
    else:
        raise ValueError(f"Unsupported SMS alert item type: {item_type}")
    return {
        "1": name,
        "2": f"{quantity:g} kg",
        "3": urgency,
        "4": area,
        "5": view_url,
        **(
            {
                "6": item.pickup_address or "Contact seller for pickup address",
            }
            if item_type == "product"
            else {}
        ),
    }


def build_demand_alert_template_variables(demand: Demand) -> Optional[dict[str, str]]:
    return build_alert_template_variables(demand, "demand")


def next_retry_time(attempt_count: int) -> datetime:
    delay_seconds = min(60 * (2 ** max(0, attempt_count - 1)), 3600)
    return datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)


def record_sms_failure(
    notification: DemandSmsNotification, error: SmsDeliveryError
) -> None:
    notification.status = "unknown" if error.outcome_unknown else "failed"
    notification.failure_reason = str(error)
    notification.next_attempt_at = None
    if (
        error.retryable
        and notification.attempt_count < settings.SMS_ALERT_MAX_ATTEMPTS
    ):
        notification.next_attempt_at = next_retry_time(notification.attempt_count)
