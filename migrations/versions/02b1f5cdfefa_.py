"""empty message

Revision ID: 02b1f5cdfefa
Revises: d4b372f76728
Create Date: 2022-01-20 18:03:56.039650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02b1f5cdfefa'
down_revision = 'd4b372f76728'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ockovaci_zarizeni', sa.Column('prakticky_lekar_deti', sa.Boolean(), nullable=True))
    op.add_column('ockovaci_zarizeni', sa.Column('prakticky_lekar_dospeli', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ockovaci_zarizeni', 'prakticky_lekar_dospeli')
    op.drop_column('ockovaci_zarizeni', 'prakticky_lekar_deti')
    # ### end Alembic commands ###