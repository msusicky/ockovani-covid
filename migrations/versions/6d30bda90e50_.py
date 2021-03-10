"""empty message

Revision ID: 6d30bda90e50
Revises: 6250e85015d1
Create Date: 2021-03-10 21:07:00.451236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d30bda90e50'
down_revision = '6250e85015d1'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("update ockovani_lide set zarizeni_kod=lpad(zarizeni_kod,11,'0')")


def downgrade():
    pass
