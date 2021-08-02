"""empty message

Revision ID: ebc18e6bef86
Revises: dd9f6e3ad7c1
Create Date: 2021-08-02 22:37:15.845527

"""
import csv
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from app.models import OckovaciMistoBezRegistrace

revision = 'ebc18e6bef86'
down_revision = 'dd9f6e3ad7c1'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("truncate table ockovaci_mista_bez_registrace")
    with open('data/ockovani_bezregistracni_centra.csv', mode='r', encoding='utf-8') as bezreg_file:
        reader = csv.reader(bezreg_file, delimiter=';')
        next(reader, None)
        bezreg_arr = [{'id': row[0], 'status': True if row[1]==1 else False, 'nazev': row[2], 'kraj': row[3], 'kraj_kod': row[4], 'nrpzs_kod': row[5], 'pouzite_vakciny': row[6], 'adresa': row[7], 'otviraci_doba': row[8], 'web': row[9], 'kontakt_tel': row[10], 'api_fronta': row[11], 'latitude': row[12], 'longitude': row[13], 'dotaz_ockovani': row[14] } for row in reader]
    op.bulk_insert(OckovaciMistoBezRegistrace.__table__, bezreg_arr)



def downgrade():
    pass
