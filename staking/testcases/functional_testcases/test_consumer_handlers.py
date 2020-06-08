import unittest
from datetime import datetime as dt
from staking.application.handlers.consumer_handlers import approve_stake_consumer_handler
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.models import StakeHolder as StakeHolderDBModel
from staking.infrastructure.models import StakeWindow as StakeWindowDBModel
from staking.infrastructure.models import StakeTransaction as StakeTransactionDBModel

stake_holder_repo = StakeHolderRepository()
stake_window_repo = StakeWindowRepository()


class TestConsumerHandler(unittest.TestCase):
    def setUp(self):
        pass

    def test_submit_stake_event_consumer(self):
        self.tearDown()
        stake_holder_repo.add_item(
            StakeHolderDBModel(
                blockchain_id=2,
                staker="0x46EF7d49aaA68B29C227442BDbD18356415f8304",
                amount_pending_for_approval=100,
                amount_approved=200,
                auto_renewal=True,
                block_no_created=12345,
                refund_amount=24567,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_window_repo.add_item(
            StakeWindowDBModel(
                blockchain_id=2,
                start_period=int(dt.utcnow().timestamp()) - 350000,
                submission_end_period=int(dt.utcnow().timestamp()) - 250000,
                approval_end_period=int(dt.utcnow().timestamp()) - 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) - 50000,
                end_period=int(dt.utcnow().timestamp()) - 10000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
                open_for_external=True,
                total_stake=70000,
                reward_amount=5000,
                token_operator="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {'data': {'row_id': 6, 'block_no': 7437812, 'event': 'ApproveStake',
                          'json_str': "{'stakeIndex': 2, 'staker': '0x46EF7d49aaA68B29C227442BDbD18356415f8304', 'tokenOperator': '0x2e9c6C4145107cD21fCDc7319E4b24a8FF636c6B', 'approvedStakeAmount': 750000000, 'returnAmount': 0}",
                          'processed': 0,
                          'transactionHash': '0xde4eb0ef752bbee94a7c82f731af0e475107a8d66abbb695174628aad7a3a1d7',
                          'logIndex': '8', 'error_code': 200, 'error_msg': '', 'row_updated': '2020-03-04 15:53:41',
                          'row_created': '2020-03-04 15:53:41'}, 'name': 'SubmitStake'}
        response = approve_stake_consumer_handler(event, None)

    def tearDown(self):
        stake_holder_repo.session.query(StakeHolderDBModel).delete()
        stake_holder_repo.session.query(StakeTransactionDBModel).delete()
        stake_holder_repo.session.query(StakeWindowDBModel).delete()
