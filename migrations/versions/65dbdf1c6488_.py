"""empty message

Revision ID: 65dbdf1c6488
Revises: d83e53594e41
Create Date: 2021-02-26 23:05:16.015712

"""
import csv

from alembic import op

# revision identifiers, used by Alembic.
from app.models import Kraj, Okres

revision = '65dbdf1c6488'
down_revision = 'd83e53594e41'
branch_labels = None
depends_on = None


def upgrade():
    with open('data/UI_VUSC.csv', mode='r', encoding='utf-8') as kraje_file:
        reader = csv.reader(kraje_file, delimiter=';')
        next(reader, None)
        kraje_arr = [{'id': row[3], 'nazev': row[1]} for row in reader]

    print(kraje_arr)

    op.bulk_insert(Kraj.__table__, kraje_arr)

    with open('data/UI_OKRES.csv', mode='r', encoding='utf-8') as okresy_file:
        reader = csv.reader(okresy_file, delimiter=';')
        next(reader, None)
        okresy_arr = [{'id': row[3], 'nazev': row[1], 'kraj_id': row[3][0:5]} for row in reader]

    print(okresy_arr)

    op.bulk_insert(Okres.__table__, okresy_arr)


def downgrade():
    pass
