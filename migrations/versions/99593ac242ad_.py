"""empty message

Revision ID: 99593ac242ad
Revises: c703c687dcbf
Create Date: 2021-04-14 20:28:39.139451

"""
import pandas as pd
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99593ac242ad'
down_revision = 'c703c687dcbf'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    df = pd.read_csv('./data/dodavky_vakcin/2021-04-14.csv')
    df['datum'] = pd.to_datetime(df['Měsíc'], format='%d. %m. %Y')
    df = df.rename({'AZ': 'AstraZeneca'}, axis=1)
    df = df.melt(id_vars=['datum'],
                 value_vars=['Pfizer', 'Moderna', 'AstraZeneca', 'CureVac', 'Janssen', 'Novavax', 'GSK'],
                 var_name='vyrobce', value_name='pocet')
    df.to_sql('dodavky_vakcin', connection, if_exists='replace', index=False)


def downgrade():
    pass
