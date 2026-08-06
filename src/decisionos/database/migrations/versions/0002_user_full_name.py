"""add full name to users

Revision ID: 0002_user_full_name
Revises: 0001_identity_users
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_user_full_name"
down_revision = "0001_identity_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("full_name", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "full_name")
