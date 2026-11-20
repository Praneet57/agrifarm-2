from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


class DemandSmsNotification(Base):
    __tablename__ = "demand_sms_notifications"
    __table_args__ = (
        UniqueConstraint("demand_id", "recipient_id", name="uq_demand_sms_recipient"),
        UniqueConstraint("product_id", "recipient_id", name="uq_product_sms_recipient"),
        CheckConstraint(
            "(demand_id IS NOT NULL AND product_id IS NULL) OR "
            "(demand_id IS NULL AND product_id IS NOT NULL)",
            name="ck_demand_sms_exactly_one_source",
        ),
        Index("ix_demand_sms_dispatch", "status", "next_attempt_at", "dispatch_claimed_at"),
    )

    id = Column(Integer, primary_key=True)
    demand_id = Column(
        Integer, ForeignKey("demands.id", ondelete="CASCADE"), nullable=True
    )
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    recipient_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String(24), nullable=False, default="queued", server_default="queued")
    attempt_count = Column(Integer, nullable=False, default=0, server_default="0")
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    next_attempt_at = Column(DateTime(timezone=True), nullable=True)
    dispatch_claimed_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    provider_updated_at = Column(DateTime(timezone=True), nullable=True)
    provider_status = Column(String(24), nullable=True)
    provider_message_id = Column(String(100), nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )
