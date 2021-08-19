"""empty message

Revision ID: 130cce777d35
Revises: b8e5763ba835
Create Date: 2021-08-19 17:22:18.183208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '130cce777d35'
down_revision = 'b8e5763ba835'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_ockovani_lide_profese_kraj_bydl_nuts', table_name='ockovani_lide_profese')
    op.drop_index('ix_ockovani_lide_profese_kraj_nuts_kod', table_name='ockovani_lide_profese')
    op.drop_index('ix_ockovani_lide_profese_zarizeni_kod', table_name='ockovani_lide_profese')
    op.drop_table('ockovani_lide_profese')
    op.add_column('ockovani_lide', sa.Column('indikace_bezpecnostni_infrastruktura', sa.Boolean(), nullable=True))
    op.add_column('ockovani_lide', sa.Column('indikace_chronicke_onemocneni', sa.Boolean(), nullable=True))
    op.add_column('ockovani_lide', sa.Column('indikace_ostatni', sa.Boolean(), nullable=True))
    op.add_column('ockovani_lide', sa.Column('indikace_pedagog', sa.Boolean(), nullable=True))
    op.add_column('ockovani_lide', sa.Column('indikace_skolstvi_ostatni', sa.Boolean(), nullable=True))
    op.add_column('ockovani_lide', sa.Column('indikace_socialni_sluzby', sa.Boolean(), nullable=True))
    op.add_column('ockovani_lide', sa.Column('indikace_zdravotnik', sa.Boolean(), nullable=True))
    op.add_column('ockovani_lide', sa.Column('kraj_bydl_nuts', sa.Unicode(), nullable=True))
    op.execute("UPDATE ockovani_lide SET indikace_bezpecnostni_infrastruktura=false, indikace_chronicke_onemocneni=false, indikace_ostatni=false, indikace_pedagog=false, indikace_skolstvi_ostatni=false, indikace_socialni_sluzby=false, indikace_zdravotnik=false, kraj_bydl_nuts=''")
    op.alter_column('ockovani_lide', 'indikace_bezpecnostni_infrastruktura', nullable=True)
    op.alter_column('ockovani_lide', 'indikace_chronicke_onemocneni', nullable=True)
    op.alter_column('ockovani_lide', 'indikace_ostatni', nullable=True)
    op.alter_column('ockovani_lide', 'indikace_pedagog', nullable=True)
    op.alter_column('ockovani_lide', 'indikace_skolstvi_ostatni', nullable=True)
    op.alter_column('ockovani_lide', 'indikace_socialni_sluzby', nullable=True)
    op.alter_column('ockovani_lide', 'indikace_zdravotnik', nullable=True)
    op.alter_column('ockovani_lide', 'kraj_bydl_nuts', nullable=True)
    op.create_index(op.f('ix_ockovani_lide_kraj_bydl_nuts'), 'ockovani_lide', ['kraj_bydl_nuts'], unique=False)
    op.drop_column('ockovani_lide', 'kraj_nazev')
    connection = op.get_bind()
    connection.execute("alter table ockovani_lide drop CONSTRAINT ockovani_lide_pkey")
    connection.execute("alter table ockovani_lide add CONSTRAINT ockovani_lide_pkey PRIMARY KEY (datum, vakcina, zarizeni_kod, poradi_davky, vekova_skupina, kraj_bydl_nuts, indikace_bezpecnostni_infrastruktura, indikace_chronicke_onemocneni, indikace_ostatni, indikace_pedagog, indikace_skolstvi_ostatni, indikace_socialni_sluzby, indikace_zdravotnik)")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    connection = op.get_bind()
    connection.execute("alter table ockovani_lide drop CONSTRAINT ockovani_lide_pkey")
    connection.execute("alter table ockovani_lide add CONSTRAINT ockovani_lide_pkey PRIMARY KEY (datum, vakcina, zarizeni_kod, poradi_davky, vekova_skupina)")
    op.add_column('ockovani_lide', sa.Column('kraj_nazev', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_ockovani_lide_kraj_bydl_nuts'), table_name='ockovani_lide')
    op.drop_column('ockovani_lide', 'kraj_bydl_nuts')
    op.drop_column('ockovani_lide', 'indikace_zdravotnik')
    op.drop_column('ockovani_lide', 'indikace_socialni_sluzby')
    op.drop_column('ockovani_lide', 'indikace_skolstvi_ostatni')
    op.drop_column('ockovani_lide', 'indikace_pedagog')
    op.drop_column('ockovani_lide', 'indikace_ostatni')
    op.drop_column('ockovani_lide', 'indikace_chronicke_onemocneni')
    op.drop_column('ockovani_lide', 'indikace_bezpecnostni_infrastruktura')
    op.create_table('ockovani_lide_profese',
    sa.Column('datum', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('vakcina', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('kraj_nuts_kod', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('zarizeni_kod', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('poradi_davky', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('vekova_skupina', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('kraj_bydl_nuts', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('indikace_zdravotnik', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('indikace_socialni_sluzby', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('indikace_ostatni', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('indikace_pedagog', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('indikace_skolstvi_ostatni', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('pocet', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('indikace_bezpecnostni_infrastruktura', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('indikace_chronicke_onemocneni', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('datum', 'vakcina', 'zarizeni_kod', 'poradi_davky', 'vekova_skupina', 'kraj_bydl_nuts', 'indikace_zdravotnik', 'indikace_socialni_sluzby', 'indikace_ostatni', 'indikace_pedagog', 'indikace_skolstvi_ostatni', 'indikace_bezpecnostni_infrastruktura', 'indikace_chronicke_onemocneni', name='ockovani_lide_profese_pkey')
    )
    op.create_index('ix_ockovani_lide_profese_zarizeni_kod', 'ockovani_lide_profese', ['zarizeni_kod'], unique=False)
    op.create_index('ix_ockovani_lide_profese_kraj_nuts_kod', 'ockovani_lide_profese', ['kraj_nuts_kod'], unique=False)
    op.create_index('ix_ockovani_lide_profese_kraj_bydl_nuts', 'ockovani_lide_profese', ['kraj_bydl_nuts'], unique=False)
    # ### end Alembic commands ###
