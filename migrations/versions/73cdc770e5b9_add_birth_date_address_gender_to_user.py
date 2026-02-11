"""add birth_date address gender to user

Revision ID: 73cdc770e5b9
Revises: 
Create Date: 2025-09-15 02:40:27.970760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73cdc770e5b9'
down_revision: Union[str, Sequence[str], None] = None  # This is the first migration; if prior manual tables existed adjust accordingly.
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema adding new user profile fields.

    We assume tables already exist (created previously via create_all). So we only add
    the new columns birth_date, address, gender. Operations are idempotent-ish via try/except
    to allow re-running locally without breaking if column already exists.
    """
    # SQLite lacks IF NOT EXISTS for ADD COLUMN inside Alembic; wrap in try blocks.
    for col in [
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('address', sa.String(length=255)),
        sa.Column('gender', sa.String(length=40), nullable=True),
    ]:
        try:
            op.add_column('users', col)
        except Exception:
            pass


def downgrade() -> None:
    """Downgrade schema by dropping newly added columns.

    Note: SQLite cannot drop columns easily; this will be a no-op for SQLite.
    """
    dialect = op.get_bind().dialect.name
    if dialect != 'sqlite':
        for col in ['gender', 'address', 'birth_date']:
            try:
                op.drop_column('users', col)
            except Exception:
                pass
