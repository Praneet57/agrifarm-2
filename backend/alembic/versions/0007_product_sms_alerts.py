"""Support SMS broadcasts for product listings."""
from alembic import op
import sqlalchemy as sa

revision = "0007_product_sms_alerts"
down_revision = "0006_demand_sms_alerts"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("demand_sms_notifications", "demand_id",
                    existing_type=sa.Integer(), nullable=True)
    op.add_column("demand_sms_notifications",
                  sa.Column("product_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_demand_sms_notifications_product_id_products",
        "demand_sms_notifications", "products", ["product_id"], ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_product_sms_recipient", "demand_sms_notifications",
        ["product_id", "recipient_id"],
    )
    op.create_check_constraint(
        "ck_demand_sms_exactly_one_source", "demand_sms_notifications",
        "(demand_id IS NOT NULL AND product_id IS NULL) OR "
        "(demand_id IS NULL AND product_id IS NOT NULL)",
    )


def downgrade():
    op.drop_constraint("ck_demand_sms_exactly_one_source",
                       "demand_sms_notifications", type_="check")
    op.drop_constraint("uq_product_sms_recipient",
                       "demand_sms_notifications", type_="unique")
    op.drop_constraint("fk_demand_sms_notifications_product_id_products",
                       "demand_sms_notifications", type_="foreignkey")
    op.drop_column("demand_sms_notifications", "product_id")
    op.alter_column("demand_sms_notifications", "demand_id",
                    existing_type=sa.Integer(), nullable=False)
