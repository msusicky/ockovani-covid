"""empty message

Revision ID: dd9f6e3ad7c1
Revises: 2e27c559bc25
Create Date: 2021-07-22 09:22:36.062579

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'dd9f6e3ad7c1'
down_revision = '2e27c559bc25'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('bezregistrace_fronta',
    sa.Column('bezregistrace_id', sa.Unicode(), nullable=False),
    sa.Column('cas_mereni', sa.DateTime(), nullable=False),
    sa.Column('hodnota', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('bezregistrace_id', 'cas_mereni')
    ) 
    connection = op.get_bind()
    connection.execute(text("truncate table ockovani_lide"))
    connection.execute(text("update vakciny set vakcina='Spikevax' where vyrobce='Moderna'"))


def downgrade():
    op.drop_table('bezregistrace_fronta') 
