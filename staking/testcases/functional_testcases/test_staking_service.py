import json
from unittest import TestCase
from datetime import datetime as dt
from staking.application.handlers.stake_handler import get_stake_window, \
    get_stake_holder_details_for_active_stake_window, get_stake_holder_details_for_claim_stake_windows, \
    get_all_transactions_of_stake_holder_for_given_address, get_all_stake_windows, get_stake_summary, \
    get_stake_calculator_details
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_holder_details_repository import StakeHolderDetailsRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository
from staking.infrastructure.models import StakeHolder, StakeWindow, StakeTransaction, StakeHolderDetails

stake_holder_repo = StakeHolderRepository()
stake_holder_details_repo = StakeHolderDetailsRepository()
stake_window_repo = StakeWindowRepository()
stake_transaction_repo = StakeTransactionRepository()


class TestStakingService(TestCase):
    def setUp(self):
        pass

    def test_get_stake_summary(self):
        self.tearDown()
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=100,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) + 50000,
                approval_end_period=int(dt.utcnow().timestamp()) + 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) + 200000,
                end_period=int(dt.utcnow().timestamp()) + 300000,
                min_stake=10000,
                open_for_external=True,
                total_stake=70000,
                reward_amount=5000,
                token_operator="0xq23we4r5t6y7u8i9o0w2e3r4t5y6u7i89o",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_holder_repo.add_item(
            StakeHolder(
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=100000,
                amount_approved=50000,
                block_no_created=12345678,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_holder_details_repo.add_item(
            StakeHolderDetails(
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_staked=100000,
                reward_amount=50000,
                claimable_amount=0,
                refund_amount=0,
                auto_renewal=True,
                block_no_created=12345678,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "path": "/stake-summary",
            "httpMethod": "GET"
        }
        response = get_stake_summary(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["total_reward"] == 5000)
        assert (response_body["data"]["total_stake_deposited"] == 70000)
        assert (response_body["data"]["no_of_stakers"] == 1)

    def tearDown(self):
        stake_holder_repo.session.query(StakeHolder).delete()
        stake_holder_details_repo.session.query(StakeHolderDetails).delete()
        stake_window_repo.session.query(StakeWindow).delete()
        stake_window_repo.session.query(StakeTransaction).delete()
        stake_holder_repo.session.commit()
        stake_holder_details_repo.session.commit()
        stake_window_repo.session.commit()
        stake_transaction_repo.session.commit()
