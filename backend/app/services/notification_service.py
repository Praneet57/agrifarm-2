import httpx
import json
import logging
from urllib.parse import urlparse
from app.core.config import settings

logger = logging.getLogger(__name__)


class SmsProviderNotConfigured(Exception):
    pass


class SmsDeliveryError(Exception):
    def __init__(
        self, message: str, *, retryable: bool, outcome_unknown: bool = False
    ):
        super().__init__(message)
        self.retryable = retryable
        self.outcome_unknown = outcome_unknown


def _twilio_configuration_ready(
    *, require_template: bool = False, template_sid: str = ""
) -> None:
    if not all((
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
        settings.TWILIO_PHONE_NUMBER,
    )):
        raise SmsProviderNotConfigured("SMS provider credentials or sender are not configured")
    if require_template and not template_sid:
        raise SmsProviderNotConfigured("Approved SMS content template is not configured")


async def _send_twilio_message(
    data: dict[str, str], *, require_template: bool = False
) -> tuple[str, str]:
    template_sid = data.get("ContentSid", "")
    _twilio_configuration_ready(
        require_template=require_template, template_sid=template_sid
    )
    if template_sid:
        public_url = settings.APP_PUBLIC_URL.strip().rstrip("/")
        parsed_pub = urlparse(public_url)
        if not parsed_pub.netloc:
            raise SmsProviderNotConfigured("APP_PUBLIC_URL is required for delivery callbacks")
        if not settings.DEBUG and parsed_pub.scheme != "https":
            raise SmsProviderNotConfigured("HTTPS APP_PUBLIC_URL is required for delivery callbacks")
        data["StatusCallback"] = f"{public_url}/api/v1/sms/twilio/status"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                data=data,
                timeout=10,
            )
        except httpx.TimeoutException as exc:
            raise SmsDeliveryError(
                "SMS provider request timed out",
                retryable=False,
                outcome_unknown=True,
            ) from exc
        except httpx.HTTPError as exc:
            raise SmsDeliveryError(
                "SMS provider request failed",
                retryable=False,
                outcome_unknown=True,
            ) from exc

    if response.status_code != 201:
        raise SmsDeliveryError(
            f"SMS provider returned HTTP {response.status_code}",
            retryable=response.status_code == 429,
            outcome_unknown=response.status_code >= 500,
        )
    try:
        response_data = response.json()
        message_id = response_data["sid"]
        provider_status = response_data["status"]
        if not isinstance(message_id, str) or not message_id:
            raise ValueError("Invalid SMS message ID")
        if not isinstance(provider_status, str) or not provider_status:
            raise ValueError("Invalid SMS delivery status")
        return message_id, provider_status
    except (ValueError, KeyError, TypeError) as exc:
        raise SmsDeliveryError(
            "SMS provider response did not contain a message ID",
            retryable=False,
            outcome_unknown=True,
        ) from exc


async def send_sms(to_phone: str, message: str) -> bool:
    try:
        await _send_twilio_message({
            "To": to_phone,
            "From": settings.TWILIO_PHONE_NUMBER,
            "Body": message,
        })
    except SmsProviderNotConfigured as exc:
        logger.warning("SMS not sent: %s", exc)
        return False
    except SmsDeliveryError as exc:
        logger.warning("SMS delivery failed: %s", exc)
        return False
    return True


async def send_demand_alert_sms(
    to_phone: str, template_variables: dict[str, str]
) -> tuple[str, str]:
    return await _send_twilio_message({
        "To": to_phone,
        "From": settings.TWILIO_PHONE_NUMBER,
        "ContentSid": settings.TWILIO_CONTENT_TEMPLATE_SID,
        "ContentVariables": json.dumps(template_variables),
    }, require_template=True)

async def send_product_alert_sms(
    to_phone: str, template_variables: dict[str, str]
) -> tuple[str, str]:
    return await _send_twilio_message({
        "To": to_phone,
        "From": settings.TWILIO_PHONE_NUMBER,
        "ContentSid": settings.TWILIO_PRODUCT_TEMPLATE_SID,
        "ContentVariables": json.dumps(template_variables),
    }, require_template=True)


async def notify_order_event(order_number:str, status:str, farmer_phone:str=None, buyer_phone:str=None):
    msgs={"pending":"AgriMarket: New order #{n} placed!","accepted":"AgriMarket: Order #{n} accepted!","paid":"AgriMarket: Payment confirmed for order #{n}.","delivered":"AgriMarket: Order #{n} delivered. Please confirm receipt.","completed":"AgriMarket: Order #{n} complete. Thank you!"}
    msg=msgs.get(status,f"AgriMarket: Order #{order_number} updated to {status}.").replace("{n}",order_number)
    if farmer_phone: await send_sms(farmer_phone, msg)
    if buyer_phone: await send_sms(buyer_phone, msg)
