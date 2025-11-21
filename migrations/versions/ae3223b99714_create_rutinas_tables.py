"""create_rutinas_tables

Revision ID: ae3223b99714
Revises: create_clases_table_1
Create Date: 2025-10-21 23:40:43.706334

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae3223b99714'
down_revision: Union[str, Sequence[str], None] = 'create_clases_table_1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ejercicios table (exercise catalog)
    op.create_table(
        'ejercicios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('body_section', sa.Enum('pecho', 'espalda', 'hombros', 'brazos', 'piernas', 'abdomen', 'gluteos', 'cardio', 'funcional', 'estiramiento', name='bodysection'), nullable=False),
        sa.Column('exercise_type', sa.Enum('fuerza', 'cardio', 'flexibilidad', 'funcional', 'hiit', 'core', name='exercisetype'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ejercicios_name'), 'ejercicios', ['name'], unique=True)
    op.create_index(op.f('ix_ejercicios_body_section'), 'ejercicios', ['body_section'], unique=False)

    # Create rutinas table (routine assignments)
    op.create_table(
        'rutinas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_by_coach_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_coach_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rutinas_user_id'), 'rutinas', ['user_id'], unique=False)
    op.create_index(op.f('ix_rutinas_created_by_coach_id'), 'rutinas', ['created_by_coach_id'], unique=False)

    # Create rutina_ejercicios table (junction table with exercise configuration)
    op.create_table(
        'rutina_ejercicios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rutina_id', sa.Integer(), nullable=False),
        sa.Column('ejercicio_id', sa.Integer(), nullable=False),
        sa.Column('series', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('repeticiones', sa.String(length=40), nullable=True),
        sa.Column('peso', sa.String(length=40), nullable=True),
        sa.Column('descanso', sa.String(length=40), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['rutina_id'], ['rutinas.id'], ),
        sa.ForeignKeyConstraint(['ejercicio_id'], ['ejercicios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rutina_ejercicios_rutina_id'), 'rutina_ejercicios', ['rutina_id'], unique=False)
    op.create_index(op.f('ix_rutina_ejercicios_ejercicio_id'), 'rutina_ejercicios', ['ejercicio_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_rutina_ejercicios_ejercicio_id'), table_name='rutina_ejercicios')
    op.drop_index(op.f('ix_rutina_ejercicios_rutina_id'), table_name='rutina_ejercicios')
    op.drop_table('rutina_ejercicios')
    
    op.drop_index(op.f('ix_rutinas_created_by_coach_id'), table_name='rutinas')
    op.drop_index(op.f('ix_rutinas_user_id'), table_name='rutinas')
    op.drop_table('rutinas')
    
    op.drop_index(op.f('ix_ejercicios_body_section'), table_name='ejercicios')
    op.drop_index(op.f('ix_ejercicios_name'), table_name='ejercicios')
    op.drop_table('ejercicios')
    
    op.execute('DROP TYPE IF EXISTS bodysection')
    op.execute('DROP TYPE IF EXISTS exercisetype')
