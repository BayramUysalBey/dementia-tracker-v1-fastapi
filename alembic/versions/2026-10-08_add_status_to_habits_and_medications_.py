"""add status to habits and medications, medication_type to enum

Revision ID: 47a93b988c4d
Revises: 6193c2af2eb4
Create Date: 2026-10-08 14:36:39.816746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '47a93b988c4d'
down_revision: Union[str, Sequence[str], None] = '6193c2af2eb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    record_status = sa.Enum('active', 'paused', 'discontinued', name='record_status')
    medication_type = sa.Enum('Pill', 'Liquid', 'Injection', name='medication_type')

    # 1. create the PostgreSQL types before any column references them
    record_status.create(op.get_bind(), checkfirst=True)
    medication_type.create(op.get_bind(), checkfirst=True)

    # 2. add the status columns, with a server-side default so the DB
    #    can satisfy NOT NULL without relying on the Python default
    op.add_column(
        'habits',
        sa.Column('status', record_status, nullable=False, server_default='active'),
    )
    op.add_column(
        'medications',
        sa.Column('status', record_status, nullable=False, server_default='active'),
    )

    # 3. convert medication_type; PostgreSQL needs an explicit cast
    op.alter_column(
        'medications',
        'medication_type',
        existing_type=sa.VARCHAR(length=255),
        type_=medication_type,
        existing_nullable=False,
        postgresql_using='medication_type::medication_type',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'medications',
        'medication_type',
        existing_type=sa.Enum('Pill', 'Liquid', 'Injection', name='medication_type'),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
        postgresql_using='medication_type::text',
    )

    op.drop_column('medications', 'status')
    op.drop_column('habits', 'status')

    sa.Enum(name='medication_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='record_status').drop(op.get_bind(), checkfirst=True)