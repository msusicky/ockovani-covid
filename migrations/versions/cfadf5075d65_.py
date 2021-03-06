"""empty message

Revision ID: cfadf5075d65
Revises: cfca0dbd30f3
Create Date: 2021-03-06 22:14:46.242202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfadf5075d65'
down_revision = 'cfca0dbd30f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ockovani_distribuce', sa.Column('pocet_davek', sa.Integer(), nullable=True))
    op.add_column('ockovani_spotreba', sa.Column('pouzite_davky', sa.Integer(), nullable=True))
    op.add_column('ockovani_spotreba', sa.Column('znehodnocene_davky', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ockovani_spotreba', 'znehodnocene_davky')
    op.drop_column('ockovani_spotreba', 'pouzite_davky')
    op.drop_column('ockovani_distribuce', 'pocet_davek')
    # ### end Alembic commands ###
