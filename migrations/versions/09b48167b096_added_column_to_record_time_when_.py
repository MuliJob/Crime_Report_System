"""Added column to record time when officer was assigned

Revision ID: 09b48167b096
Revises: 3b00345cba21
Create Date: 2024-07-22 12:32:47.771845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09b48167b096'
down_revision = '3b00345cba21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('case_report', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table('crime', schema=None) as batch_op:
        batch_op.alter_column('arrest_history',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crime', schema=None) as batch_op:
        batch_op.alter_column('arrest_history',
               existing_type=sa.TEXT(),
               nullable=False)

    with op.batch_alter_table('case_report', schema=None) as batch_op:
        batch_op.drop_column('assigned_at')

    # ### end Alembic commands ###
