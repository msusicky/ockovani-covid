"""empty message

Revision ID: a3fb0e170fc6
Revises: 518096119dae
Create Date: 2021-09-21 19:35:31.350273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3fb0e170fc6'
down_revision = '518096119dae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cr_metriky', sa.Column('ockovani_pocet_3', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('ockovani_pocet_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('ockovani_pocet_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_3', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_3', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_cekajici_3', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_cekajici_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_cekajici_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_kapacita_3', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_kapacita_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_kapacita_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici_3', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_kapacita_3', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_kapacita_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_kapacita_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_cekajici_3', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_cekajici_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_cekajici_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_kapacita_3', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_kapacita_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_kapacita_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici_3', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici_3_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_kapacita_3', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_kapacita_3_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_kapacita_3_zmena_tyden', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_3_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_3_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_3')
    op.drop_column('kraje_metriky', 'ockovani_pocet_3_zmena_tyden')
    op.drop_column('kraje_metriky', 'ockovani_pocet_3_zmena_den')
    op.drop_column('kraje_metriky', 'ockovani_pocet_3')
    op.drop_column('cr_metriky', 'ockovani_pocet_3_zmena_tyden')
    op.drop_column('cr_metriky', 'ockovani_pocet_3_zmena_den')
    op.drop_column('cr_metriky', 'ockovani_pocet_3')
    op.drop_column('okresy_metriky', 'rezervace_kapacita_3_zmena_tyden')
    op.drop_column('okresy_metriky', 'rezervace_kapacita_3_zmena_den')
    op.drop_column('okresy_metriky', 'rezervace_kapacita_3')
    op.drop_column('okresy_metriky', 'rezervace_cekajici_3_zmena_tyden')
    op.drop_column('okresy_metriky', 'rezervace_cekajici_3_zmena_den')
    op.drop_column('okresy_metriky', 'rezervace_cekajici_3')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_kapacita_3_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_kapacita_3_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_kapacita_3')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_cekajici_3_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_cekajici_3_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_cekajici_3')
    op.drop_column('kraje_metriky', 'rezervace_kapacita_3_zmena_tyden')
    op.drop_column('kraje_metriky', 'rezervace_kapacita_3_zmena_den')
    op.drop_column('kraje_metriky', 'rezervace_kapacita_3')
    op.drop_column('kraje_metriky', 'rezervace_cekajici_3_zmena_tyden')
    op.drop_column('kraje_metriky', 'rezervace_cekajici_3_zmena_den')
    op.drop_column('kraje_metriky', 'rezervace_cekajici_3')
    op.drop_column('cr_metriky', 'rezervace_kapacita_3_zmena_tyden')
    op.drop_column('cr_metriky', 'rezervace_kapacita_3_zmena_den')
    op.drop_column('cr_metriky', 'rezervace_kapacita_3')
    op.drop_column('cr_metriky', 'rezervace_cekajici_3_zmena_tyden')
    op.drop_column('cr_metriky', 'rezervace_cekajici_3_zmena_den')
    op.drop_column('cr_metriky', 'rezervace_cekajici_3')
    # ### end Alembic commands ###
