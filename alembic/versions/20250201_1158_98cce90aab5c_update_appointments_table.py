"""update_appointments_table

Revision ID: 98cce90aab5c
Revises: 
Create Date: 2025-02-01 11:58:43.972415

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '98cce90aab5c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_leads_id', table_name='leads')
    op.drop_table('leads')
    op.add_column('appointments', sa.Column('duration', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('appointments', 'duration')
    op.create_table('leads',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('source', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('status', postgresql.ENUM('NUEVO', 'CONTACTADO', 'INTERESADO', 'CONVERTIDO', 'PERDIDO', name='leadstatus'), autoincrement=False, nullable=True),
    sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='leads_pkey')
    )
    op.create_index('ix_leads_id', 'leads', ['id'], unique=False)
    # ### end Alembic commands ###