"""empty message

Revision ID: 25ebc99f8107
Revises: 12811ace3d10
Create Date: 2021-05-05 21:24:51.713714

"""
import pandas as pd
from alembic import op

# revision identifiers, used by Alembic.
revision = '25ebc99f8107'
down_revision = '12811ace3d10'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    df = pd.read_csv('data/populace.csv', delimiter=';')
    df = pd.melt(df, id_vars=['vek'], var_name='orp_kod', value_name='pocet')
    df.to_sql('populace', connection, if_exists='replace', index=False)


def downgrade():
    pass
