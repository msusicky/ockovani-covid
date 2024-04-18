"""empty message

Revision ID: 1ed9516441be
Revises: 97b4fcf044a0
Create Date: 2021-04-28 20:22:57.797639

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '1ed9516441be'
down_revision = '97b4fcf044a0'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(text("alter table ockovani_registrace add column ockovani smallint default -1"))
    connection.execute(text("alter table ockovani_registrace drop CONSTRAINT ockovani_registrace_part_pkey"))
    connection.execute(text("alter table ockovani_registrace add CONSTRAINT ockovani_registrace_part_pkey PRIMARY KEY (datum, ockovaci_misto_id, vekova_skupina, povolani, stat, rezervace, datum_rezervace, import_id, ockovani)"))


def downgrade():
    connection = op.get_bind()
    connection.execute(text("alter table ockovani_registrace drop column ockovani"))
    connection.execute(text("alter table ockovani_registrace drop CONSTRAINT ockovani_registrace_part_pkey"))
    connection.execute(text("alter table ockovani_registrace add CONSTRAINT ockovani_registrace_part_pkey PRIMARY KEY (datum, ockovaci_misto_id, vekova_skupina, povolani, stat, rezervace, datum_rezervace, import_id)"))
