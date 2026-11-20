from celery import Celery
from datetime import datetime, timezone
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("agri", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
celery_app.conf.update(task_serializer="json", accept_content=["json"], timezone="Asia/Kolkata", enable_utc=True,
    beat_schedule={
        "expire-demands": {"task": "app.workers.tasks.expire_old_demands", "schedule": 3600.0},
        "dispatch-demand-sms": {"task": "app.workers.tasks.dispatch_demand_sms", "schedule": 15.0},
    })

@celery_app.task(name="app.workers.tasks.send_sms_task")
def send_sms_task(phone: str, message: str):
    import asyncio
    from app.services.notification_service import send_sms
    asyncio.run(send_sms(phone, message))


@celery_app.task(name="app.workers.tasks.dispatch_demand_sms")
def dispatch_demand_sms():
    import asyncio

    async def _run():
        from app.core.database import AsyncSessionLocal
        from app.services.demand_alert_service import claim_notifications_for_dispatch

        async with AsyncSessionLocal() as db:
            notification_ids = await claim_notifications_for_dispatch(db)
        for notification_id in notification_ids:
            try:
                send_demand_sms_notification.delay(notification_id)
            except Exception:
                logger.exception(
                    "Unable to enqueue demand SMS notification %s", notification_id
                )

    asyncio.run(_run())


@celery_app.task(name="app.workers.tasks.send_demand_sms_notification")
def send_demand_sms_notification(notification_id: int):
    import asyncio

    async def _run():
        from sqlalchemy import select
        from app.core.database import AsyncSessionLocal
        from app.models.demand import Demand
        from app.models.demand_notification import DemandSmsNotification
        from app.models.product import Product
        from app.models.user import User
        from app.services.demand_alert_service import (
            build_alert_template_variables,
            haversine_distance_km,
            normalize_indian_mobile,
            record_sms_failure,
        )
        from app.services.notification_service import (
            SmsDeliveryError,
            SmsProviderNotConfigured,
            send_demand_alert_sms,
            send_product_alert_sms,
        )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(DemandSmsNotification)
                .where(DemandSmsNotification.id == notification_id)
                .with_for_update()
            )
            notification = result.scalar_one_or_none()
            if not notification or notification.status != "queued":
                return

            notification.status = "sending"
            notification.dispatch_claimed_at = None
            notification.attempt_count += 1
            notification.next_attempt_at = None
            notification.last_attempt_at = datetime.now(timezone.utc)
            if notification.demand_id is not None:
                item_result = await db.execute(select(Demand).where(Demand.id == notification.demand_id))
                item = item_result.scalar_one_or_none()
                item_type = "demand"
            else:
                item_result = await db.execute(select(Product).where(Product.id == notification.product_id))
                item = item_result.scalar_one_or_none()
                item_type = "product"
            user_result = await db.execute(
                select(User).where(User.id == notification.recipient_id)
            )
            recipient = user_result.scalar_one_or_none()
            owner_id = (item.buyer_id if item_type == "demand" else item.farmer_id) if item else None
            item_is_active = bool(item and item.is_active and (
                (item_type == "demand" and item.is_urgent and item.allow_location_based_alerts and item.status == "open")
                or (item_type == "product" and item.status == "available")
            ))
            allowed_roles = (
                {"farmer", "buyer"}
                if item_type == "product" or settings.SMS_ALERT_RECIPIENT_ROLE == "all"
                else {settings.SMS_ALERT_RECIPIENT_ROLE}
            )

            eligible = bool(
                item
                and item_is_active
                and recipient
                and recipient.id != owner_id
                and recipient.is_active
                and recipient.is_verified
                and recipient.sms_alerts_opt_in
                and recipient.role in allowed_roles
                and (
                    item_type == "product"
                    or (
                        recipient.share_location_for_alerts
                        and recipient.latitude is not None
                        and recipient.longitude is not None
                        and item.latitude is not None
                        and item.longitude is not None
                        and haversine_distance_km(
                            item.latitude,
                            item.longitude,
                            recipient.latitude,
                            recipient.longitude,
                        ) <= 10.0
                    )
                )
            )
            if not eligible:
                notification.status = "skipped"
                notification.failure_reason = "Recipient or demand no longer eligible"
                await db.commit()
                return
            destination_phone = normalize_indian_mobile(recipient.phone)
            if not destination_phone:
                notification.status = "failed"
                notification.failure_reason = "Recipient phone is not a valid Indian mobile number"
                await db.commit()
                return

            template_variables = build_alert_template_variables(item, item_type)
            if not template_variables:
                notification.status = "not_configured"
                notification.failure_reason = "APP_PUBLIC_URL is not configured"
                await db.commit()
                return

            await db.commit()
            try:
                sender = send_demand_alert_sms if item_type == "demand" else send_product_alert_sms
                provider_message_id, provider_status = await sender(
                    destination_phone, template_variables
                )
            except SmsProviderNotConfigured as exc:
                notification.status = "not_configured"
                notification.failure_reason = str(exc)
                await db.commit()
                return
            except SmsDeliveryError as exc:
                record_sms_failure(notification, exc)
                await db.commit()
                logger.warning(
                    "SMS alert notification %s failed: %s",
                    notification_id,
                    exc,
                )
                return
            except Exception:
                notification.status = "unknown"
                notification.failure_reason = "Unexpected SMS delivery outcome"
                await db.commit()
                logger.exception(
                    "Unexpected error delivering SMS alert notification %s",
                    notification_id,
                )
                raise

            notification.status = "submitted"
            notification.sent_at = datetime.now(timezone.utc)
            notification.provider_message_id = provider_message_id
            notification.provider_status = provider_status
            notification.provider_updated_at = notification.sent_at
            notification.failure_reason = None
            notification.next_attempt_at = None
            await db.commit()

    asyncio.run(_run())


@celery_app.task(name="app.workers.tasks.generate_agreement_task")
def generate_agreement_task(order_id: int):
    import asyncio
    async def _run():
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import select
        from app.models.order import Order
        from app.models.payment import Agreement
        from app.services.pdf_service import generate_agreement_pdf
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Order).where(Order.id==order_id))
            order = result.scalar_one_or_none()
            if order:
                pdf_path = await generate_agreement_pdf(order, db)
                ex = await db.execute(select(Agreement).where(Agreement.order_id==order_id))
                ag = ex.scalar_one_or_none()
                if not ag: ag = Agreement(order_id=order_id, pdf_key=pdf_path); db.add(ag)
                else: ag.pdf_key = pdf_path
                await db.commit()
    asyncio.run(_run())

@celery_app.task(name="app.workers.tasks.expire_old_demands")
def expire_old_demands():
    import asyncio
    async def _run():
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import update, or_, and_
        from app.models.demand import Demand
        from datetime import datetime, timedelta
        async with AsyncSessionLocal() as db:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            await db.execute(
                update(Demand).where(
                    Demand.status == "open",
                    Demand.is_active == True,
                    or_(
                        Demand.required_by < now,
                        and_(
                            Demand.required_by == None,
                            Demand.created_at < thirty_days_ago,
                        ),
                    ),
                ).values(status="expired")
            )
            await db.commit()
    asyncio.run(_run())
