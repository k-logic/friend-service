"""remove_persona_from_invitation

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-27 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('invitation_tokens_persona_id_fkey', 'invitation_tokens', type_='foreignkey')
    op.drop_column('invitation_tokens', 'persona_id')


def downgrade() -> None:
    op.add_column('invitation_tokens', sa.Column('persona_id', sa.Integer(), nullable=True))
    op.create_foreign_key('invitation_tokens_persona_id_fkey', 'invitation_tokens', 'personas', ['persona_id'], ['id'])
