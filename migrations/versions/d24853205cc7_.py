"""empty message

Revision ID: d24853205cc7
Revises: f636a63c48d6
Create Date: 2021-11-17 17:26:01.984058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd24853205cc7'
down_revision = 'f636a63c48d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ockovaci_mista_detail', sa.Column('davky', sa.ARRAY(sa.Integer()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ockovaci_mista_detail', 'davky')
    # ### end Alembic commands ###
