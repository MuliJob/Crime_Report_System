"""removed initial column

Revision ID: f1ad4d5fc033
Revises: 4f6c82449db6
Create Date: 2024-07-04 16:12:44.714381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1ad4d5fc033'
down_revision = '4f6c82449db6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('case_report', schema=None) as batch_op:
        batch_op.drop_column('assigned_officer')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('case_report', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assigned_officer', sa.VARCHAR(length=40), nullable=True))

    # ### end Alembic commands ###
