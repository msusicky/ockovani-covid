"""empty message

Revision ID: f238461c71d7
Revises: ed6702f505d7
Create Date: 2021-03-14 08:50:38.037321

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'f238461c71d7'
down_revision = 'ed6702f505d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_1', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_1_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_1_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_2', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_2_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_2_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('ockovani_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('pocet_obyvatel_celkem', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('pocet_obyvatel_dospeli', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_celkem', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_celkem_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_fronta', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_fronta_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_prumer_cekani', sa.Float(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_prumer_cekani_zmena_den', sa.Float(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_tydenni_uspesnost', sa.Float(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('registrace_tydenni_uspesnost_zmena_den', sa.Float(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_cekajici_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_celkem', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('rezervace_celkem_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_ockovane_pocet', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_ockovane_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_ockovane_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_prijate_pocet', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_prijate_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_prijate_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_vydane_pocet', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_vydane_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_vydane_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_znicene_pocet', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_znicene_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('kraje_metriky', sa.Column('vakciny_znicene_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.drop_column('kraje_metriky', 'hodnota_str')
    op.drop_column('kraje_metriky', 'typ_metriky')
    op.drop_column('kraje_metriky', 'hodnota_int')
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_1', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_1_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_1_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_2', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_2_zmena_den', sa.Integer(), nullable=True))
    op.add_column('ockovaci_mista_metriky', sa.Column('ockovani_pocet_2_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('pocet_obyvatel_celkem', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('pocet_obyvatel_dospeli', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_celkem', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_celkem_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_fronta', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_fronta_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_prumer_cekani', sa.Float(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_prumer_cekani_zmena_den', sa.Float(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_tydenni_uspesnost', sa.Float(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('registrace_tydenni_uspesnost_zmena_den', sa.Float(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_cekajici_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_celkem', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('rezervace_celkem_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_ockovane_pocet', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_ockovane_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_ockovane_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_prijate_pocet', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_prijate_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_prijate_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_vydane_pocet', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_vydane_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_vydane_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_znicene_pocet', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_znicene_pocet_zmena_den', sa.Integer(), nullable=True))
    op.add_column('okresy_metriky', sa.Column('vakciny_znicene_pocet_zmena_tyden', sa.Integer(), nullable=True))
    op.drop_column('okresy_metriky', 'hodnota_str')
    op.drop_column('okresy_metriky', 'typ_metriky')
    op.drop_column('okresy_metriky', 'hodnota_int')
    connection = op.get_bind()
    connection.execute(text("truncate table ockovaci_mista_metriky"))
    connection.execute(text("truncate table okresy_metriky"))
    connection.execute(text("truncate table kraje_metriky"))
    op.add_column('kraje_metriky', sa.Column('kraj_id', sa.Unicode(), nullable=False))
    op.drop_constraint('kraje_metriky_id_fkey', 'kraje_metriky', type_='foreignkey')
    op.create_foreign_key(None, 'kraje_metriky', 'kraje', ['kraj_id'], ['id'])
    op.drop_column('kraje_metriky', 'id')
    op.add_column('ockovaci_mista_metriky', sa.Column('misto_id', sa.Unicode(), nullable=False))
    op.drop_constraint('ockovaci_mista_metriky_id_fkey', 'ockovaci_mista_metriky', type_='foreignkey')
    op.create_foreign_key(None, 'ockovaci_mista_metriky', 'ockovaci_mista', ['misto_id'], ['id'])
    op.drop_column('ockovaci_mista_metriky', 'id')
    op.add_column('okresy_metriky', sa.Column('okres_id', sa.Unicode(), nullable=False))
    op.drop_constraint('okresy_metriky_id_fkey', 'okresy_metriky', type_='foreignkey')
    op.create_foreign_key(None, 'okresy_metriky', 'okresy', ['okres_id'], ['id'])
    op.drop_column('okresy_metriky', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('okresy_metriky', sa.Column('hodnota_int', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('okresy_metriky', sa.Column('typ_metriky', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('okresy_metriky', sa.Column('hodnota_str', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('okresy_metriky', 'vakciny_znicene_pocet_zmena_tyden')
    op.drop_column('okresy_metriky', 'vakciny_znicene_pocet_zmena_den')
    op.drop_column('okresy_metriky', 'vakciny_znicene_pocet')
    op.drop_column('okresy_metriky', 'vakciny_vydane_pocet_zmena_tyden')
    op.drop_column('okresy_metriky', 'vakciny_vydane_pocet_zmena_den')
    op.drop_column('okresy_metriky', 'vakciny_vydane_pocet')
    op.drop_column('okresy_metriky', 'vakciny_prijate_pocet_zmena_tyden')
    op.drop_column('okresy_metriky', 'vakciny_prijate_pocet_zmena_den')
    op.drop_column('okresy_metriky', 'vakciny_prijate_pocet')
    op.drop_column('okresy_metriky', 'vakciny_ockovane_pocet_zmena_tyden')
    op.drop_column('okresy_metriky', 'vakciny_ockovane_pocet_zmena_den')
    op.drop_column('okresy_metriky', 'vakciny_ockovane_pocet')
    op.drop_column('okresy_metriky', 'rezervace_celkem_zmena_den')
    op.drop_column('okresy_metriky', 'rezervace_celkem')
    op.drop_column('okresy_metriky', 'rezervace_cekajici_zmena_den')
    op.drop_column('okresy_metriky', 'rezervace_cekajici')
    op.drop_column('okresy_metriky', 'registrace_tydenni_uspesnost_zmena_den')
    op.drop_column('okresy_metriky', 'registrace_tydenni_uspesnost')
    op.drop_column('okresy_metriky', 'registrace_prumer_cekani_zmena_den')
    op.drop_column('okresy_metriky', 'registrace_prumer_cekani')
    op.drop_column('okresy_metriky', 'registrace_fronta_zmena_den')
    op.drop_column('okresy_metriky', 'registrace_fronta')
    op.drop_column('okresy_metriky', 'registrace_celkem_zmena_den')
    op.drop_column('okresy_metriky', 'registrace_celkem')
    op.drop_column('okresy_metriky', 'pocet_obyvatel_dospeli')
    op.drop_column('okresy_metriky', 'pocet_obyvatel_celkem')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_2_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_2_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_2')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_1_zmena_tyden')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_1_zmena_den')
    op.drop_column('ockovaci_mista_metriky', 'ockovani_pocet_1')
    op.add_column('kraje_metriky', sa.Column('hodnota_int', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('kraje_metriky', sa.Column('typ_metriky', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('kraje_metriky', sa.Column('hodnota_str', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('kraje_metriky', 'vakciny_znicene_pocet_zmena_tyden')
    op.drop_column('kraje_metriky', 'vakciny_znicene_pocet_zmena_den')
    op.drop_column('kraje_metriky', 'vakciny_znicene_pocet')
    op.drop_column('kraje_metriky', 'vakciny_vydane_pocet_zmena_tyden')
    op.drop_column('kraje_metriky', 'vakciny_vydane_pocet_zmena_den')
    op.drop_column('kraje_metriky', 'vakciny_vydane_pocet')
    op.drop_column('kraje_metriky', 'vakciny_prijate_pocet_zmena_tyden')
    op.drop_column('kraje_metriky', 'vakciny_prijate_pocet_zmena_den')
    op.drop_column('kraje_metriky', 'vakciny_prijate_pocet')
    op.drop_column('kraje_metriky', 'vakciny_ockovane_pocet_zmena_tyden')
    op.drop_column('kraje_metriky', 'vakciny_ockovane_pocet_zmena_den')
    op.drop_column('kraje_metriky', 'vakciny_ockovane_pocet')
    op.drop_column('kraje_metriky', 'rezervace_celkem_zmena_den')
    op.drop_column('kraje_metriky', 'rezervace_celkem')
    op.drop_column('kraje_metriky', 'rezervace_cekajici_zmena_den')
    op.drop_column('kraje_metriky', 'rezervace_cekajici')
    op.drop_column('kraje_metriky', 'registrace_tydenni_uspesnost_zmena_den')
    op.drop_column('kraje_metriky', 'registrace_tydenni_uspesnost')
    op.drop_column('kraje_metriky', 'registrace_prumer_cekani_zmena_den')
    op.drop_column('kraje_metriky', 'registrace_prumer_cekani')
    op.drop_column('kraje_metriky', 'registrace_fronta_zmena_den')
    op.drop_column('kraje_metriky', 'registrace_fronta')
    op.drop_column('kraje_metriky', 'registrace_celkem_zmena_den')
    op.drop_column('kraje_metriky', 'registrace_celkem')
    op.drop_column('kraje_metriky', 'pocet_obyvatel_dospeli')
    op.drop_column('kraje_metriky', 'pocet_obyvatel_celkem')
    op.drop_column('kraje_metriky', 'ockovani_pocet_zmena_tyden')
    op.drop_column('kraje_metriky', 'ockovani_pocet_zmena_den')
    op.drop_column('kraje_metriky', 'ockovani_pocet_2_zmena_tyden')
    op.drop_column('kraje_metriky', 'ockovani_pocet_2_zmena_den')
    op.drop_column('kraje_metriky', 'ockovani_pocet_2')
    op.drop_column('kraje_metriky', 'ockovani_pocet_1_zmena_tyden')
    op.drop_column('kraje_metriky', 'ockovani_pocet_1_zmena_den')
    op.drop_column('kraje_metriky', 'ockovani_pocet_1')
    op.drop_column('kraje_metriky', 'ockovani_pocet')
    op.add_column('okresy_metriky', sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'okresy_metriky', type_='foreignkey')
    op.create_foreign_key('okresy_metriky_id_fkey', 'okresy_metriky', 'okresy', ['id'], ['id'])
    op.drop_column('okresy_metriky', 'okres_id')
    op.add_column('ockovaci_mista_metriky', sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'ockovaci_mista_metriky', type_='foreignkey')
    op.create_foreign_key('ockovaci_mista_metriky_id_fkey', 'ockovaci_mista_metriky', 'ockovaci_mista', ['id'], ['id'])
    op.drop_column('ockovaci_mista_metriky', 'misto_id')
    op.add_column('kraje_metriky', sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'kraje_metriky', type_='foreignkey')
    op.create_foreign_key('kraje_metriky_id_fkey', 'kraje_metriky', 'kraje', ['id'], ['id'])
    op.drop_column('kraje_metriky', 'kraj_id')
    # ### end Alembic commands ###
