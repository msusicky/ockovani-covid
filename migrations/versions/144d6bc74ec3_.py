"""empty message

Revision ID: 144d6bc74ec3
Revises: 02b1f5cdfefa
Create Date: 2022-03-15 18:45:12.605591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '144d6bc74ec3'
down_revision = '02b1f5cdfefa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reinfekce',
    sa.Column('datum', sa.Date(), nullable=False),
    sa.Column('pocet', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('datum')
    )

    op.execute("update vakciny set vakcina='Nuvaxovid', aktivni=true where vyrobce='Novavax'")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reinfekce')
    # ### end Alembic commands ###
