"""testing_another_way

Revision ID: 6efa14fb8fa3
Revises: 8e611aa99e15
Create Date: 2026-03-15 17:31:08.001791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6efa14fb8fa3'
down_revision: Union[str, Sequence[str], None] = '8e611aa99e15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
