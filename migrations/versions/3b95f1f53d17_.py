"""empty message

Revision ID: 3b95f1f53d17
Revises: 85eff7d60dbe
Create Date: 2024-04-22 10:58:23.537441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b95f1f53d17'
down_revision = '85eff7d60dbe'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni, nemoc) VALUES('Adacel', 'Adacel', 1, 'Adacel', true, 'Černý kašel')")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni, nemoc) VALUES('Adacel Polio', 'Adacel Polio', 1, 'Adacel Polio', true, 'Černý kašel')")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni, nemoc) VALUES('Boostrix', 'Boostrix', 1, 'Boostrix', true, 'Černý kašel')")
    op.execute("update vakciny set aktivni = false where vyrobce in ('AstraZeneca', 'AstraZenecaIN', 'BharatBiotech', 'Covovax', 'CureVac', 'Sinopharm', 'Sinovac', 'Sputnik V', 'Valneva')")
    op.execute("update vakciny set aktivni = true where vyrobce = 'Janssen'")


def downgrade():
    pass
