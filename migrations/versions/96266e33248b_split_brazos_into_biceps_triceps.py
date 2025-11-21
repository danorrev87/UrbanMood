"""split_brazos_into_biceps_triceps

Revision ID: 96266e33248b
Revises: ae3223b99714
Create Date: 2025-10-22 14:55:35.922761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96266e33248b'
down_revision: Union[str, Sequence[str], None] = 'ae3223b99714'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Split 'brazos' category into 'biceps' and 'triceps' to match gym paper forms."""
    # SQLite doesn't support ALTER TYPE for enums, so we need to work with string values
    # Update existing 'brazos' exercises to either 'biceps' or 'triceps' based on exercise type
    
    # First, update bicep exercises (IDs 13-14 from seed data)
    op.execute("""
        UPDATE ejercicios 
        SET body_section = 'biceps' 
        WHERE id IN (13, 14)
    """)
    
    # Update tricep exercises (IDs 15-16 from seed data)
    op.execute("""
        UPDATE ejercicios 
        SET body_section = 'triceps' 
        WHERE id IN (15, 16)
    """)


def downgrade() -> None:
    """Merge 'biceps' and 'triceps' back into 'brazos'."""
    op.execute("""
        UPDATE ejercicios 
        SET body_section = 'brazos' 
        WHERE body_section IN ('biceps', 'triceps')
    """)
