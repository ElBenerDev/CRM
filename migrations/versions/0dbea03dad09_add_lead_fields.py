"""add_lead_fields

Revision ID: 0dbea03dad09
Revises: 393e7bc9f15d
Create Date: 2025-01-25 21:05:00.462081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dbea03dad09'
down_revision: Union[str, None] = '393e7bc9f15d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Agregar nuevas columnas a la tabla leads
    op.add_column('leads', sa.Column('source', sa.String(), nullable=True))
    op.add_column('leads', sa.Column('interest', sa.String(), nullable=True))
    op.add_column('leads', sa.Column('priority', sa.String(), server_default='media', nullable=False))

def downgrade():
    # Eliminar las columnas en caso de rollback
    op.drop_column('leads', 'priority')
    op.drop_column('leads', 'interest')
    op.drop_column('leads', 'source')