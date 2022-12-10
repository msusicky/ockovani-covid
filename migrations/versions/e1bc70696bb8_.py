"""empty message

Revision ID: e1bc70696bb8
Revises: 60211c3d0790
Create Date: 2022-09-16 18:05:47.576580

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e1bc70696bb8'
down_revision = '60211c3d0790'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('PfizerBA.1', 'Comirnaty Original/Omicron BA.1', 1, 'Pfizer3', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('PfizerBA.45', 'Comirnaty Original/Omicron BA.4/BA.5', 1, 'Pfizer4', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('ModernaBA.1', 'Spikevax bivalent Original/Omicron BA.1', 1, 'Moderna2', true) ON CONFLICT (vakcina) DO NOTHING")


def downgrade():
    pass
