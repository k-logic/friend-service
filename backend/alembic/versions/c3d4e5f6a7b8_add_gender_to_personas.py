"""add_gender_to_personas

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-27 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    gender_enum = sa.Enum('male', 'female', name='gender')
    gender_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('personas', sa.Column('gender', gender_enum, nullable=True))


def downgrade() -> None:
    op.drop_column('personas', 'gender')
    sa.Enum(name='gender').drop(op.get_bind(), checkfirst=True)
