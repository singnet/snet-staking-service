"""baseline

Revision ID: 4ce108ce2ebb
Revises: 
Create Date: 2020-03-31 13:13:29.615450

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4ce108ce2ebb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stake_window',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('blockchain_id', sa.Integer(), nullable=False),
                    sa.Column('start_period', sa.Integer(), nullable=False),
                    sa.Column('submission_end_period', sa.Integer(), nullable=False),
                    sa.Column('approval_end_period', sa.Integer(), nullable=False),
                    sa.Column('request_withdraw_start_period', sa.Integer(), nullable=False),
                    sa.Column('end_period', sa.Integer(), nullable=False),
                    sa.Column('min_stake', mysql.BIGINT(), nullable=False),
                    sa.Column('open_for_external', sa.BOOLEAN(), nullable=False),
                    sa.Column('total_stake', mysql.BIGINT(), nullable=False),
                    sa.Column('reward_amount', mysql.BIGINT(), nullable=False),
                    sa.Column('token_operator', mysql.VARCHAR(length=50), nullable=False),
                    sa.Column('created_on', mysql.TIMESTAMP(), nullable=False),
                    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('blockchain_id', name='uq_stake_window')
                    )
    op.create_table('stake_holder',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('staker', mysql.VARCHAR(length=50), nullable=False),
                    sa.Column('amount_pending_for_approval', mysql.BIGINT(), nullable=False),
                    sa.Column('amount_approved', mysql.BIGINT(), nullable=False),
                    sa.Column('block_no_created', sa.Integer(), nullable=False),
                    sa.Column('created_on', mysql.TIMESTAMP(), nullable=False),
                    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('staker', name='uq_sh')
                    )
    op.create_table('stake_holder_details',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('blockchain_id', sa.Integer(), nullable=False),
                    sa.Column('staker', mysql.VARCHAR(length=50), nullable=False),
                    sa.Column('amount_staked', mysql.BIGINT(), nullable=False),
                    sa.Column('reward_amount', mysql.BIGINT(), nullable=False),
                    sa.Column('claimable_amount', mysql.BIGINT(), nullable=False),
                    sa.Column('refund_amount', mysql.BIGINT(), nullable=False),
                    sa.Column('auto_renewal', sa.BOOLEAN(), nullable=False),
                    sa.Column('block_no_created', sa.Integer(), nullable=False),
                    sa.Column('created_on', mysql.TIMESTAMP(), nullable=False),
                    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('blockchain_id', 'staker', name='uq_shd')
                    )
    op.create_table('stake_transaction',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('blockchain_id', sa.Integer(), nullable=False),
                    sa.Column('staker', mysql.VARCHAR(length=50), nullable=True),
                    sa.Column('event', mysql.VARCHAR(length=128), nullable=False),
                    sa.Column('event_data', mysql.JSON(), nullable=False),
                    sa.Column('block_no', sa.Integer(), nullable=False),
                    sa.Column('transaction_hash', mysql.VARCHAR(length=128), nullable=False),
                    sa.Column('transaction_date', mysql.TIMESTAMP(), nullable=False),
                    sa.Column('created_on', mysql.TIMESTAMP(), nullable=False),
                    sa.Column('updated_on', mysql.TIMESTAMP(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stake_window')
    op.drop_table('stake_holder')
    op.drop_table('stake_holder_details')
    op.drop_table('stake_transaction')
    # ### end Alembic commands ###
