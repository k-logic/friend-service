"""足跡にユニーク制約追加

Revision ID: 0e08274ff9c4
Revises: c3d4e5f6a7b8
Create Date: 2026-02-27 01:10:49.051408

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0e08274ff9c4"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_footprints_visitor_persona", "footprints", ["visitor_account_id", "persona_id"])


def downgrade() -> None:
    op.drop_constraint("uq_footprints_visitor_persona", "footprints", type_="unique")
