"""empty message

Revision ID: 5480e96df417
Revises: 2a85252aeb80
Create Date: 2021-09-26 21:45:13.993879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5480e96df417'
down_revision = '2a85252aeb80'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("DELETE FROM populace_kategorie WHERE vekova_skupina='0-17'")
    connection.execute("INSERT INTO populace_kategorie (vekova_skupina,min_vek,max_vek) VALUES ('0-11',0,11)")
    connection.execute("INSERT INTO populace_kategorie (vekova_skupina,min_vek,max_vek) VALUES ('12-15',12,15)")
    connection.execute("INSERT INTO populace_kategorie (vekova_skupina,min_vek,max_vek) VALUES ('16-17',16,17)")


def downgrade():
    connection = op.get_bind()
    connection.execute("DELETE FROM populace_kategorie WHERE vekova_skupina='0-11'")
    connection.execute("DELETE FROM populace_kategorie WHERE vekova_skupina='12-15'")
    connection.execute("DELETE FROM populace_kategorie WHERE vekova_skupina='16-17'")
    connection.execute("INSERT INTO populace_kategorie (vekova_skupina,min_vek,max_vek) VALUES ('0-17',0,17)")
