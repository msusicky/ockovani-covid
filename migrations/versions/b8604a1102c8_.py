"""empty message

Revision ID: b8604a1102c8
Revises: 5406a27a7927
Create Date: 2021-03-08 20:59:27.677584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8604a1102c8'
down_revision = '5406a27a7927'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("delete from importy where status='FAILED'")
    connection.execute("delete from importy where id in (select id from importy except select max(id) from importy group by date)")

def downgrade():
    pass
