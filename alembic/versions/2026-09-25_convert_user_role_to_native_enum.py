"""convert user role to native enum

Revision ID: 6193c2af2eb4
Revises: a5d515ddaf44
Create Date: 2026-09-25 16:00:57.204410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6193c2af2eb4'
down_revision: Union[str, Sequence[str], None] = 'a5d515ddaf44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role = sa.Enum(
        'caregiver', 'patient', 'family', 'doctor',
        name='user_role',
    )
    user_role.create(op.get_bind(), checkfirst=True)

    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.execute("""
        UPDATE users
        SET role = 'caregiver'
        WHERE role NOT IN ('caregiver', 'patient', 'family', 'doctor')
    """)

    op.alter_column(
        'users',
        'role',
        existing_type=sa.String(length=255),
        type_=user_role,
        existing_nullable=False,
        postgresql_using='role::user_role',
    )

    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'caregiver'::user_role")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.alter_column(
        'users',
        'role',
        existing_type=sa.Enum(name='user_role'),
        type_=sa.String(length=255),
        existing_nullable=False,
        postgresql_using='role::text'
    )

    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'caregiver'")
    sa.Enum(name='user_role').drop(op.get_bind(), checkfirst=True)
