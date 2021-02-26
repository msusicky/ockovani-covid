"""empty message

Revision ID: acfabd93055e
Revises: 6dfd4b41bc2e
Create Date: 2021-02-26 16:34:17.397892

"""
import csv

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import MetaData, Table

from app.models import Kraj, Okres

revision = 'acfabd93055e'
down_revision = '6dfd4b41bc2e'
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
