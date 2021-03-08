"""empty message

Revision ID: 6250e85015d1
Revises: 73729bd3913e
Create Date: 2021-03-08 21:20:34.281169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6250e85015d1'
down_revision = '73729bd3913e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('kraje_metriky',
    sa.Column('id', sa.Unicode(), nullable=False),
    sa.Column('datum', sa.DateTime(), nullable=False),
    sa.Column('typ_metriky', sa.Unicode(), nullable=False),
    sa.Column('hodnota_int', sa.Integer(), nullable=True),
    sa.Column('hodnota_str', sa.Unicode(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['kraje.id'], ),
    sa.PrimaryKeyConstraint('id', 'datum', 'typ_metriky')
    )
    op.create_table('okresy_metriky',
    sa.Column('id', sa.Unicode(), nullable=False),
    sa.Column('datum', sa.DateTime(), nullable=False),
    sa.Column('typ_metriky', sa.Unicode(), nullable=False),
    sa.Column('hodnota_int', sa.Integer(), nullable=True),
    sa.Column('hodnota_str', sa.Unicode(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['okresy.id'], ),
    sa.PrimaryKeyConstraint('id', 'datum', 'typ_metriky')
    )
    op.create_table('ockovaci_mista_metriky',
    sa.Column('id', sa.Unicode(), nullable=False),
    sa.Column('datum', sa.DateTime(), nullable=False),
    sa.Column('typ_metriky', sa.Unicode(), nullable=False),
    sa.Column('hodnota_int', sa.Integer(), nullable=True),
    sa.Column('hodnota_str', sa.Unicode(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['ockovaci_mista.id'], ),
    sa.PrimaryKeyConstraint('id', 'datum', 'typ_metriky')
    )
    op.add_column('ockovani_registrace', sa.Column('pocet_zmena', sa.Integer(), nullable=True))
    op.add_column('ockovani_rezervace', sa.Column('maximalni_kapacita_zmena', sa.Integer(), nullable=True))
    op.add_column('ockovani_rezervace', sa.Column('volna_kapacita_zmena', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ockovani_rezervace', 'volna_kapacita_zmena')
    op.drop_column('ockovani_rezervace', 'maximalni_kapacita_zmena')
    op.drop_column('ockovani_registrace', 'pocet_zmena')
    op.drop_table('ockovaci_mista_metriky')
    op.drop_table('okresy_metriky')
    op.drop_table('kraje_metriky')
    # ### end Alembic commands ###
