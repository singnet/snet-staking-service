"""new_staked_amount column added in stake_holder table

Revision ID: ca19bc99f23c
Revises: 4ce108ce2ebb
Create Date: 2020-04-27 14:03:54.625253

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ca19bc99f23c'
down_revision = '4ce108ce2ebb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stake_holder', sa.Column('new_staked_amount', mysql.BIGINT(), nullable=False, default=0))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stake_holder', 'new_staked_amount')
    # ### end Alembic commands ###
