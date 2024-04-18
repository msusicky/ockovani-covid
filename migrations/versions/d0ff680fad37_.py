"""empty message

Revision ID: d0ff680fad37
Revises: 18f99a103a26
Create Date: 2021-06-30 20:24:32.012301

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'd0ff680fad37'
down_revision = '18f99a103a26'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(text("update praktici_kapacity set adresa=split_part(adresa, ',', 1)"))


def downgrade():
    pass
