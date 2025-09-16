"""create clases table

Revision ID: create_clases_table_1
Revises: 73cdc770e5b9
Create Date: 2025-09-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'create_clases_table_1'
down_revision: Union[str, Sequence[str], None] = '73cdc770e5b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'clases',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
    )
    op.create_index('ix_clases_name', 'clases', ['name'], unique=True)
    op.create_index('ix_clases_is_active', 'clases', ['is_active'])


def downgrade() -> None:
    op.drop_index('ix_clases_name', table_name='clases')
    op.drop_index('ix_clases_is_active', table_name='clases')
    op.drop_table('clases')
