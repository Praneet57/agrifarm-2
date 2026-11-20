"""Add additional product photos and video.
Revision ID: 0005_product_media
Revises: 0004_customer_support
Create Date: 2026-10-21 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_product_media"
down_revision = "0004_customer_support"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "products",
        sa.Column("image_urls", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.add_column(
        "products",
        sa.Column("video_url", sa.String(length=500), nullable=True),
    )


def downgrade():
    op.drop_column("products", "video_url")
    op.drop_column("products", "image_urls")
