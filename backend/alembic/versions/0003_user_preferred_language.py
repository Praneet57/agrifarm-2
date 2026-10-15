"""Store each user's preferred interface language.
Revision ID: 0003_user_preferred_language
Revises: 0002_registration_details
Create Date: 2026-10-11 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_user_preferred_language"
down_revision = "0002_registration_details"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("preferred_language", sa.String(2), nullable=False, server_default="en"),
    )


def downgrade():
    op.drop_column("users", "preferred_language")
