"""Add an explicit pickup address for product SMS alerts."""
from alembic import op
import sqlalchemy as sa

revision = "0008_product_pickup_address"
down_revision = "0007_product_sms_alerts"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "products",
        sa.Column("pickup_address", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column("products", "pickup_address")
