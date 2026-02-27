"""add_invitation_tokens

Revision ID: a1b2c3d4e5f6
Revises: b0235a46ef8f
Create Date: 2026-02-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'b0235a46ef8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('invitation_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('persona_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('used_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['used_by'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_invitation_tokens_token'), 'invitation_tokens', ['token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_invitation_tokens_token'), table_name='invitation_tokens')
    op.drop_table('invitation_tokens')
