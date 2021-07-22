"""empty message

Revision ID: f651e82d35b9
Revises: f06bc0ec884b
Create Date: 2021-07-21 23:15:14.099124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f651e82d35b9'
down_revision = 'f06bc0ec884b'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("update vakciny set vakcina='Spikevax' where vyrobce='Moderna'")



def downgrade():
    pass
