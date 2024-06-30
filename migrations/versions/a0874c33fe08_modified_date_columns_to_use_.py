"""modified date columns to use appropriate time zone and removed columns for coordinates in user table

Revision ID: a0874c33fe08
Revises: a8ab84bd668d
Create Date: 2024-06-30 16:29:30.342747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0874c33fe08'
down_revision = 'a8ab84bd668d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('latitude')
        batch_op.drop_column('longitude')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('longitude', sa.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('latitude', sa.FLOAT(), nullable=True))

    # ### end Alembic commands ###
