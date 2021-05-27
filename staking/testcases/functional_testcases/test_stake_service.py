import json
from unittest import TestCase
from datetime import datetime as dt
from staking.application.handlers.stake_handler import get_stake_window, \
    get_stake_holder_details_for_active_stake_window, get_stake_holder_details_for_claim_stake_windows, \
    get_all_transactions_of_stake_holder_for_given_address, get_all_stake_windows, get_stake_summary, \
    get_stake_calculator_details
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository
from staking.infrastructure.models import StakeHolder, StakeWindow, StakeTransaction

stake_holder_repo = StakeHolderRepository()
stake_window_repo = StakeWindowRepository()
stake_transaction_repo = StakeTransactionRepository()


class TestStakeService(TestCase):
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
                max_stake=100000,
                window_max_cap=500000,
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
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=100000,
                amount_approved=50000,
                auto_renewal=False,
                block_no_created=12345678,
                refund_amount=0,
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

    def test_get_all_stake_windows(self):
        self.tearDown()
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=100,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) - 50000,
                approval_end_period=int(dt.utcnow().timestamp()) + 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) + 200000,
                end_period=int(dt.utcnow().timestamp()) + 300000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
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
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=100000,
                amount_approved=50000,
                auto_renewal=False,
                block_no_created=12345678,
                refund_amount=0,
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
            "path": "/staking-windows",
            "httpMethod": "GET"
        }
        response = get_all_stake_windows(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["blockchain_id"] == 100)
        assert (response_body["data"][0]["no_of_stakers"] == 1)
        assert (response_body["data"][0]["reward_amount"] == 5000)
        assert (response_body["data"][0]["total_stake_deposited"] == 100000)

    def test_get_staking_window_open_for_submission(self):
        self.tearDown()
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=100,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) - 50000,
                approval_end_period=int(dt.utcnow().timestamp()) - 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) - 200000,
                end_period=int(dt.utcnow().timestamp()) - 300000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
                open_for_external=True,
                total_stake=70000,
                reward_amount=5000,
                token_operator="0xq23we4r5t6y7u8i9o0w2e3r4t5y6u7i89o",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=101,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) + 50000,
                approval_end_period=int(dt.utcnow().timestamp()) + 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) + 200000,
                end_period=int(dt.utcnow().timestamp()) + 300000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
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
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=0,
                amount_approved=100000,
                auto_renewal=True,
                block_no_created=12345678,
                refund_amount=0,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_holder_repo.add_item(
            StakeHolder(
                blockchain_id=101,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=100000,
                amount_approved=0,
                auto_renewal=False,
                block_no_created=12345679,
                refund_amount=0,
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
            "path": "/staking-window",
            "httpMethod": "GET",
            "queryStringParameters": {"status": "OPEN", "staker": "0xq2w3e4r5t6y7u8e3r45ty6u78i"}
        }
        response = get_stake_window(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["blockchain_id"] == 101)
        print(response)
        assert (response_body["data"][0]["no_of_stakers"] == 1)
        assert (response_body["data"][0]["pending_stake_amount_for_staker"] == 100000)
        assert (response_body["data"][0]["approved_stake_amount_for_staker"] == 0)
        assert (response_body["data"][0]["total_stake_deposited"] == 100000)

    def test_get_staker_details_for_active_window(self):
        self.tearDown()
        stake_holder_repo.add_item(
            StakeHolder(
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=100000,
                amount_approved=50000,
                auto_renewal=False,
                block_no_created=12345678,
                refund_amount=0,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=100,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) - 10000,
                approval_end_period=int(dt.utcnow().timestamp()) + 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) + 200000,
                end_period=int(dt.utcnow().timestamp()) + 300000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
                open_for_external=True,
                total_stake=70000,
                reward_amount=5000,
                token_operator="0xq23we4r5t6y7u8i9o0w2e3r4t5y6u7i89o",
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
            "path": "/stake-holder/active",
            "httpMethod": "GET",
            "queryStringParameters": {"status": "OPEN", "address": "0xq2w3e4r5t6y7u8e3r45ty6u78i"}
        }
        response = get_stake_holder_details_for_active_stake_window(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["stake_holder"]["blockchain_id"] == 100)
        assert (response_body["data"][0]["stake_window"]["blockchain_id"] == 100)

    def test_get_stake_holder_claims_details(self):
        self.tearDown()
        stake_holder_repo.add_item(
            StakeHolder(
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=0,
                amount_approved=150000,
                auto_renewal=False,
                block_no_created=12345678,
                refund_amount=0,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=100,
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
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=101,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) + 50000,
                approval_end_period=int(dt.utcnow().timestamp()) + 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) + 200000,
                end_period=int(dt.utcnow().timestamp()) + 300000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
                open_for_external=True,
                total_stake=70000,
                reward_amount=5000,
                token_operator="0xq23we4r5t6y7u8i9o0w2e3r4t5y6u7i89o",
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
            "path": "/stake-holder/claim",
            "httpMethod": "GET",
            "queryStringParameters": {"address": "0xq2w3e4r5t6y7u8e3r45ty6u78i"}
        }
        response = get_stake_holder_details_for_claim_stake_windows(event, None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["stake_holder"]["blockchain_id"] == 100)
        assert (response_body["data"][0]["stake_window"]["blockchain_id"] == 100)

    def test_get_all_transactions_of_stake_holder_for_given_address(self):
        self.tearDown()
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=100,
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
        stake_transaction_repo.add_item(
            StakeTransaction(
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                event="ClaimStake",
                event_data={},
                block_no=12345678,
                transaction_hash="0xawserfw3r5y7i9xdfcmknjhbr5t6",
                transaction_date=dt.utcnow(),
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
            "path": "/transactions",
            "httpMethod": "GET",
            "queryStringParameters": {"address": "0xq2w3e4r5t6y7u8e3r45ty6u78i"}
        }
        response = get_all_transactions_of_stake_holder_for_given_address(event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["stake_window"]["blockchain_id"] == 100)

    def test_get_stake_calculator_details(self):
        self.tearDown()
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=100,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) - 50000,
                approval_end_period=int(dt.utcnow().timestamp()) - 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) - 200000,
                end_period=int(dt.utcnow().timestamp()) - 300000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
                open_for_external=True,
                total_stake=70000,
                reward_amount=5000,
                token_operator="0xq23we4r5t6y7u8i9o0w2e3r4t5y6u7i89o",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_window_repo.add_item(
            StakeWindow(
                blockchain_id=101,
                start_period=int(dt.utcnow().timestamp()) - 50000,
                submission_end_period=int(dt.utcnow().timestamp()) + 50000,
                approval_end_period=int(dt.utcnow().timestamp()) + 100000,
                request_withdraw_start_period=int(dt.utcnow().timestamp()) + 200000,
                end_period=int(dt.utcnow().timestamp()) + 300000,
                min_stake=10000,
                max_stake=100000,
                window_max_cap=500000,
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
                blockchain_id=100,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=0,
                amount_approved=100000,
                auto_renewal=True,
                block_no_created=12345678,
                refund_amount=0,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        stake_holder_repo.add_item(
            StakeHolder(
                blockchain_id=101,
                staker="0xq2w3e4r5t6y7u8e3r45ty6u78i",
                amount_pending_for_approval=100000,
                amount_approved=0,
                auto_renewal=False,
                block_no_created=12345679,
                refund_amount=0,
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
            "path": "/staking-window",
            "httpMethod": "GET",
            "queryStringParameters": {"status": "OPEN", "staker": "0xq2w3e4r5t6y7u8e3r45ty6u78i"}
        }
        response = get_stake_calculator_details(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["blockchain_id"] == 101)
        assert (response_body["data"]["total_stake_pending_for_approval"] == 100000)
        assert (response_body["data"]["total_stake_approved"] == 0)
        assert (response_body["data"]["total_auto_renew_amount"] == 107142)

    def tearDown(self):
        stake_holder_repo.session.query(StakeHolder).delete()
        stake_window_repo.session.query(StakeWindow).delete()
        stake_window_repo.session.query(StakeTransaction).delete()
        stake_holder_repo.session.commit()
        stake_window_repo.session.commit()
        stake_transaction_repo.session.commit()
