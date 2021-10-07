"""empty message

Revision ID: c4ad908e06e4
Revises: 9544fe5355f8
Create Date: 2021-10-06 21:01:53.527699

"""
import pandas as pd
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c4ad908e06e4'
down_revision = '9544fe5355f8'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    df = pd.read_csv('data/populace_orp.csv', delimiter=';')
    df['orp_kod'] = df['orp_kod'].astype(str)
    df.to_sql('populace_orp', connection, if_exists='replace', index=False)


def downgrade():
    pass
