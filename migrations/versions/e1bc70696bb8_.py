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

    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('Comirnaty 6m-4', 'Comirnaty 6m-4', 2, 'Pfizer5', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('Comirnaty Omicron XBB.1.5.', 'Comirnaty Omicron XBB.1.5.', 2, 'Pfizer6', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('Comirnaty Omicron XBB.1.5. 5-11', 'Comirnaty Omicron XBB.1.5. 5-11', 2, 'Pfizer7', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('COMIRNATY OMICRON XBB.1.5 6m-4', 'COMIRNATY OMICRON XBB.1.5 6m-4', 2, 'Pfizer8', true) ON CONFLICT (vakcina) DO NOTHING")

    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('Covovax', 'Covovax', 2, 'Covovax', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('Nuvaxovid XBB 1.5', 'Nuvaxovid XBB 1.5', 2, 'Novavax2', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('SPIKEVAX BIVALENT ORIGINAL/OMICRON BA.4-5', 'SPIKEVAX BIVALENT ORIGINAL/OMICRON BA.4-5', 2, 'SPIKEVAX BIVALENT ORIGINAL/OMICRON BA.4-5', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('Sputnik V', 'Sputnik V', 2, 'Sputnik V', true) ON CONFLICT (vakcina) DO NOTHING")
    op.execute("insert into vakciny (vyrobce, vakcina, davky, vakcina_sklad, aktivni) VALUES('Valneva', 'Valneva', 2, 'Valneva', true) ON CONFLICT (vakcina) DO NOTHING")


def downgrade():
    pass
