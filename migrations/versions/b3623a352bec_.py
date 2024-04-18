"""empty message

Revision ID: b3623a352bec
Revises: 1430d11d2ce8
Create Date: 2021-03-21 16:21:32.442625

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'b3623a352bec'
down_revision = '1430d11d2ce8'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(text("INSERT INTO ockovaci_mista (id, nazev, okres_id, status, nrpzs_kod) VALUES('4561f6a6-a019-4fb6-8552-6e15c74a3d04', 'EUC klinika Ostrava', 'CZ0806', false, '25860836000')"))
    connection.execute(text("INSERT INTO ockovaci_mista (id, nazev, okres_id, status, nrpzs_kod) VALUES('68fcce7d-b37b-4073-a8a0-c21a62976442', 'VITA, s.r.o.', 'CZ0426', false, '61537713000')"))
    connection.execute(text("INSERT INTO ockovaci_mista (id, nazev, okres_id, status, nrpzs_kod) VALUES('9d29801f-7265-47cc-abfc-0167f8f58b2d', 'HNsP Bílina', 'CZ0426', false, '61325422000')"))

def downgrade():
    pass
