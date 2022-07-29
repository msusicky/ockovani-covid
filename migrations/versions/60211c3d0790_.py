"""empty message

Revision ID: 60211c3d0790
Revises: 144d6bc74ec3
Create Date: 2022-07-29 22:19:50.016901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60211c3d0790'
down_revision = '144d6bc74ec3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cr_metriky', sa.Column('ockovani_pocet_4', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('ockovani_pocet_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('ockovani_pocet_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_cekajici_4', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_cekajici_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_cekajici_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_kapacita_4', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_kapacita_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('cr_metriky', sa.Column('rezervace_kapacita_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_4', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_4_bydl', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_4_bydl_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_4_bydl_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici_4', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_kapacita_4', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_kapacita_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_kapacita_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_4', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_cekajici_4', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_cekajici_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_cekajici_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_kapacita_4', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_kapacita_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('rezervace_kapacita_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici_4', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici_4_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_kapacita_4', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_kapacita_4_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_kapacita_4_zmena_tyden', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('okresy_metriky', 'rezervace_kapacita_4_zmena_tyden')
    op.drop_column('okresy_metriky', 'rezervace_kapacita_4_zmena_den')
    op.drop_column('okresy_metriky', 'rezervace_kapacita_4')
    op.drop_column('okresy_metriky', 'rezervace_cekajici_4_zmena_tyden')
    op.drop_column('okresy_metriky', 'rezervace_cekajici_4_zmena_den')
    op.drop_column('okresy_metriky', 'rezervace_cekajici_4')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_kapacita_4_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_kapacita_4_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_kapacita_4')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_cekajici_4_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_cekajici_4_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'rezervace_cekajici_4')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_4_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_4_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_4')
    op.drop_column('kraje_metriky', 'rezervace_kapacita_4_zmena_tyden')
    op.drop_column('kraje_metriky', 'rezervace_kapacita_4_zmena_den')
    op.drop_column('kraje_metriky', 'rezervace_kapacita_4')
    op.drop_column('kraje_metriky', 'rezervace_cekajici_4_zmena_tyden')
    op.drop_column('kraje_metriky', 'rezervace_cekajici_4_zmena_den')
    op.drop_column('kraje_metriky', 'rezervace_cekajici_4')
    op.drop_column('kraje_metriky', 'ockovani_pocet_4_zmena_tyden')
    op.drop_column('kraje_metriky', 'ockovani_pocet_4_zmena_den')
    op.drop_column('kraje_metriky', 'ockovani_pocet_4_bydl_zmena_tyden')
    op.drop_column('kraje_metriky', 'ockovani_pocet_4_bydl_zmena_den')
    op.drop_column('kraje_metriky', 'ockovani_pocet_4_bydl')
    op.drop_column('kraje_metriky', 'ockovani_pocet_4')
    op.drop_column('cr_metriky', 'rezervace_kapacita_4_zmena_tyden')
    op.drop_column('cr_metriky', 'rezervace_kapacita_4_zmena_den')
    op.drop_column('cr_metriky', 'rezervace_kapacita_4')
    op.drop_column('cr_metriky', 'rezervace_cekajici_4_zmena_tyden')
    op.drop_column('cr_metriky', 'rezervace_cekajici_4_zmena_den')
    op.drop_column('cr_metriky', 'rezervace_cekajici_4')
    op.drop_column('cr_metriky', 'ockovani_pocet_4_zmena_tyden')
    op.drop_column('cr_metriky', 'ockovani_pocet_4_zmena_den')
    op.drop_column('cr_metriky', 'ockovani_pocet_4')
    # ### end Alembic commands ###
