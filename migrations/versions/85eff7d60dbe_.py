"""empty message

Revision ID: 85eff7d60dbe
Revises: fb644dbb9719
Create Date: 2024-04-20 16:45:10.728594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85eff7d60dbe'
down_revision = 'fb644dbb9719'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('praktici_kapacity', schema=None) as batch_op:
        batch_op.drop_column('kontakt_tel')
        batch_op.drop_column('kontakt_email')

    with op.batch_alter_table('praktici_login', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.Unicode(), nullable=True))
        batch_op.add_column(sa.Column('telefon', sa.Unicode(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('praktici_login', schema=None) as batch_op:
        batch_op.drop_column('telefon')
        batch_op.drop_column('email')

    with op.batch_alter_table('praktici_kapacity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('kontakt_email', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('kontakt_tel', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###