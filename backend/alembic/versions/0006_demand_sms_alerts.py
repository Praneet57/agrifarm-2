"""Add urgent demand SMS preferences and delivery tracking.
Revision ID: 0006_demand_sms_alerts
Revises: 0005_product_media
Create Date: 2026-10-27 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0006_demand_sms_alerts"
down_revision = "0005_product_media"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("sms_alerts_opt_in", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "users", sa.Column("sms_alert_consent_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "users", sa.Column("sms_alerts_opted_out_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "share_location_for_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "users",
        sa.Column("location_sharing_consent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "demands",
        sa.Column("is_urgent", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "demands",
        sa.Column(
            "allow_location_based_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index(
        "ix_users_alert_coordinates", "users", ["latitude", "longitude"], unique=False
    )
    op.create_table(
        "demand_sms_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("demand_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="queued"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dispatch_claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_status", sa.String(length=24), nullable=True),
        sa.Column("provider_message_id", sa.String(length=100), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["demand_id"], ["demands.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("demand_id", "recipient_id", name="uq_demand_sms_recipient"),
    )
    op.create_index(
        "ix_demand_sms_dispatch",
        "demand_sms_notifications",
        ["status", "next_attempt_at", "dispatch_claimed_at"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_demand_sms_dispatch", table_name="demand_sms_notifications")
    op.drop_table("demand_sms_notifications")
    op.drop_index("ix_users_alert_coordinates", table_name="users")
    op.drop_column("demands", "allow_location_based_alerts")
    op.drop_column("demands", "is_urgent")
    op.drop_column("users", "share_location_for_alerts")
    op.drop_column("users", "location_sharing_consent_at")
    op.drop_column("users", "sms_alerts_opted_out_at")
    op.drop_column("users", "sms_alert_consent_at")
    op.drop_column("users", "sms_alerts_opt_in")
