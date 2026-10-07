"""Add registration address and seller details.
Revision ID: 0002_registration_details
Revises: 0001_initial
Create Date: 2026-09-17 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_registration_details"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("taluk", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("area", sa.String(150), nullable=True))
    op.add_column("users", sa.Column("door_no_farm", sa.String(150), nullable=True))
    op.add_column("users", sa.Column("purpose", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("products_to_sell", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("products_to_buy", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("farm_type", sa.String(150), nullable=True))
    op.add_column("users", sa.Column("farm_agriculture_details", sa.String(1000), nullable=True))


def downgrade():
    op.drop_column("users", "farm_type")
    op.drop_column("users", "farm_agriculture_details")
    op.drop_column("users", "products_to_buy")
    op.drop_column("users", "products_to_sell")
    op.drop_column("users", "purpose")
    op.drop_column("users", "door_no_farm")
    op.drop_column("users", "area")
    op.drop_column("users", "taluk")
