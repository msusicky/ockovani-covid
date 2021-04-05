"""empty message

Revision ID: b3e73cf868d6
Revises: 727fc1f53f80
Create Date: 2021-04-05 20:06:07.547613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3e73cf868d6'
down_revision = '727fc1f53f80'
branch_labels = None
depends_on = None


def upgrade():
    with open("./migrations/versions/b3e73cf868d6.sql") as file_:
        for statement in file_.read().split(";"):  # \n removed ; or however we want to split
            if len(statement)>0:
                op.execute(statement)
                print(statement)
    

def downgrade():
    op.execute("alter table public.ockovani_registrace rename to ockovani_registrace_del")
    op.execute("alter table public.ockovani_registrace_old rename to ockovani_registrace")
    op.execute("drop table public.ockovani_registrace_del")

