"""add workspaces and decisions

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001_identity_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('owner_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_workspaces_owner_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_workspaces'))
    )

    # Create decisions table
    op.create_table(
        'decisions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('workspace_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2048), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'UNDER_REVIEW', 'DECIDED', 'COMPLETED', name='decisionstatus'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='decisionpriority'), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name=op.f('fk_decisions_workspace_id_workspaces')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_decisions'))
    )


def downgrade() -> None:
    op.drop_table('decisions')
    op.drop_table('workspaces')
