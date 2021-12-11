"""empty message

Revision ID: 915031b7317f
Revises: f4bb16f1a389
Create Date: 2021-12-11 10:11:04.587012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '915031b7317f'
down_revision = 'f4bb16f1a389'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("truncate table nakazeni")
    op.execute("truncate table umrti")

    op.execute('ALTER TABLE nakazeni DROP CONSTRAINT nakazeni_pkey')
    op.execute('ALTER TABLE umrti DROP CONSTRAINT umrti_pkey')

    op.add_column('nakazeni', sa.Column('vek', sa.Integer(), nullable=False))
    op.drop_column('nakazeni', 'vekova_skupina')
    op.add_column('umrti', sa.Column('vek', sa.Integer(), nullable=False))
    op.drop_column('umrti', 'vekova_skupina')

    op.create_primary_key('nakazeni_pkey', 'nakazeni', ['datum', 'vek', 'kraj_nuts_kod'])
    op.create_primary_key('umrti_pkey', 'umrti', ['datum', 'vek', 'kraj_nuts_kod'])


def downgrade():
    op.execute("truncate table nakazeni")
    op.execute("truncate table umrti")

    op.execute('ALTER TABLE nakazeni DROP CONSTRAINT nakazeni_pkey')
    op.execute('ALTER TABLE umrti DROP CONSTRAINT umrti_pkey')

    op.add_column('umrti', sa.Column('vekova_skupina', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('umrti', 'vek')
    op.add_column('nakazeni', sa.Column('vekova_skupina', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('nakazeni', 'vek')

    op.create_primary_key('nakazeni_pkey', 'nakazeni', ['datum', 'vekova_skupina', 'kraj_nuts_kod'])
    op.create_primary_key('umrti_pkey', 'umrti', ['datum', 'vekova_skupina', 'kraj_nuts_kod'])
