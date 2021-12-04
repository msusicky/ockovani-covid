"""empty message

Revision ID: f06bc0ec884b
Revises: d0ff680fad37
Create Date: 2021-07-19 21:59:21.675860

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f06bc0ec884b'
down_revision = 'd0ff680fad37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ockovaci_mista_bez_registrace',
    sa.Column('id', sa.Unicode(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('nazev', sa.Unicode(), nullable=True),
    sa.Column('kraj', sa.Unicode(), nullable=False),
    sa.Column('kraj_kod', sa.Unicode(), nullable=False),
    sa.Column('nrpzs_kod', sa.Unicode(), nullable=True),
    sa.Column('pouzite_vakciny', sa.Unicode(), nullable=True),
    sa.Column('adresa', sa.Unicode(), nullable=True),
    sa.Column('otviraci_doba', sa.Unicode(), nullable=True),
    sa.Column('web', sa.Unicode(), nullable=True),
    sa.Column('kontakt_tel', sa.Unicode(), nullable=True),
    sa.Column('api_fronta', sa.Unicode(), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('dotaz_ockovani', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###

    # with open('data/ockovani_bezregistracni_centra.csv', mode='r', encoding='utf-8') as bezreg_file:
    #     reader = csv.reader(bezreg_file, delimiter=';')
    #     next(reader, None)
    #     bezreg_arr = [{'id': row[0], 'status': True if row[1]==1 else False, 'nazev': row[2], 'kraj': row[3], 'kraj_kod': row[4], 'nrpzs_kod': row[5], 'pouzite_vakciny': row[6], 'adresa': row[7], 'otviraci_doba': row[8], 'web': row[9], 'kontakt_tel': row[10], 'api_fronta': row[11], 'latitude': row[12], 'longitude': row[13], 'dotaz_ockovani': row[14] } for row in reader]
    #
    # op.bulk_insert(OckovaciMistoBezRegistrace.__table__, bezreg_arr)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ockovaci_mista_bez_registrace')
    # ### end Alembic commands ###
