import base64
import hashlib
import hmac
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.demand_notification import DemandSmsNotification

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sms", tags=["SMS"])

ALLOWED_PROVIDER_STATUSES = {
    "accepted",
    "queued",
    "sending",
    "sent",
    "delivered",
    "undelivered",
    "failed",
    "scheduled",
}
TERMINAL_PROVIDER_STATUSES = {"delivered", "undelivered", "failed"}


def verify_twilio_signature(
    request_url: str,
    form_items: list[tuple[str, str]],
    signature: str,
    auth_token: str,
) -> bool:
    signed_data = request_url + "".join(
        key + value for key, value in sorted(form_items)
    )
    expected = base64.b64encode(
        hmac.new(
            auth_token.encode("utf-8"),
            signed_data.encode("utf-8"),
            hashlib.sha1,
        ).digest()
    ).decode("ascii")
    return hmac.compare_digest(expected, signature)


@router.post("/twilio/status", status_code=204)
async def twilio_delivery_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    if not settings.TWILIO_AUTH_TOKEN:
        raise HTTPException(503, "SMS provider webhook is not configured")

    form = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")
    public_url = settings.APP_PUBLIC_URL.strip().rstrip("/")
    parsed_pub = urlparse(public_url)
    if not parsed_pub.netloc:
        raise HTTPException(503, "APP_PUBLIC_URL is not configured")
    if not settings.DEBUG and parsed_pub.scheme != "https":
        raise HTTPException(503, "HTTPS APP_PUBLIC_URL is required in production")
    request_url = f"{public_url}{request.url.path}"
    if request.url.query:
        request_url = f"{request_url}?{request.url.query}"
    form_items = [(str(key), str(value)) for key, value in form.multi_items()]
    if not signature or not verify_twilio_signature(
        request_url, form_items, signature, settings.TWILIO_AUTH_TOKEN
    ):
        raise HTTPException(403, "Invalid SMS provider signature")

    message_id = form.get("MessageSid")
    provider_status = form.get("MessageStatus")
    if not message_id or provider_status not in ALLOWED_PROVIDER_STATUSES:
        raise HTTPException(400, "Invalid SMS delivery status payload")

    result = await db.execute(
        select(DemandSmsNotification)
        .where(DemandSmsNotification.provider_message_id == message_id)
        .with_for_update()
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        logger.warning("SMS status callback arrived before message %s was recorded", message_id)
        raise HTTPException(503, "SMS message is not recorded yet")

    if notification.status in {"delivered", "undelivered", "failed"}:
        return Response(status_code=204)

    now = datetime.now(timezone.utc)
    notification.provider_status = provider_status
    notification.provider_updated_at = now
    if provider_status == "delivered":
        notification.status = "delivered"
        notification.delivered_at = now
        notification.failure_reason = None
    elif provider_status in {"undelivered", "failed"}:
        notification.status = provider_status
        error_code = form.get("ErrorCode")
        notification.failure_reason = (
            f"Twilio delivery error code {error_code}"
            if error_code
            else f"Twilio reported {provider_status}"
        )
    else:
        notification.status = "submitted"
    await db.flush()
    return Response(status_code=204)
