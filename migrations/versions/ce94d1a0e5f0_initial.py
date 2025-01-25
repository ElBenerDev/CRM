"""initial

Revision ID: ce94d1a0e5f0
Revises: 
Create Date: 2025-01-25 12:36:25.511879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ce94d1a0e5f0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('appointments', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.alter_column('appointments', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('appointments', 'service_type',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('appointments', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.drop_index('ix_appointments_date', table_name='appointments')
    op.drop_constraint('appointments_patient_id_fkey', 'appointments', type_='foreignkey')
    op.create_foreign_key(None, 'appointments', 'patients', ['patient_id'], ['id'], ondelete='CASCADE')
    op.alter_column('patients', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_index('ix_patients_email', table_name='patients')
    op.drop_index('ix_patients_name', table_name='patients')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_patients_name', 'patients', ['name'], unique=False)
    op.create_index('ix_patients_email', 'patients', ['email'], unique=True)
    op.alter_column('patients', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_constraint(None, 'appointments', type_='foreignkey')
    op.create_foreign_key('appointments_patient_id_fkey', 'appointments', 'patients', ['patient_id'], ['id'])
    op.create_index('ix_appointments_date', 'appointments', ['date'], unique=False)
    op.alter_column('appointments', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('appointments', 'service_type',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('appointments', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('appointments', 'updated_at')
    # ### end Alembic commands ###
