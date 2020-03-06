import time
from common.logger import get_logger
import os
from common.blockchain_util import BlockChainUtil
from staking.domain.model.stake_window import StakeWindow
from staking.domain.model.stake_holder import StakeHolder
from staking.domain.model.stake_transaction import StakeTransaction
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository

logger = get_logger(__name__)
stake_window_repo = StakeWindowRepository()
stake_holder_repo = StakeHolderRepository()
stake_transaction_repo = StakeTransactionRepository()


class TokenStakeEventConsumer(object):

    def __init__(self, ws_provider, net_id):
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self._net_id = net_id

    def on_event(self, event):
        pass

    def _get_token_stake_contract(self):
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'node_modules', 'singularitynet-platform-contracts'))
        logger.info(f"base_contract_path: {base_contract_path}")
        token_stake_contract = self._blockchain_util.get_contract_instance(base_contract_path, "TokenStake",
                                                                           self._net_id)

        return token_stake_contract

    @staticmethod
    def _get_event_data(event):
        return eval(event['data']['json_str'])

    @staticmethod
    def _get_metadata_hash(metadata_uri):
        return metadata_uri.decode("utf-8")

    def _get_stake_window_by_stake_index(self, stake_index):
        token_stake_contract = self._get_token_stake_contract()
        stake_window_data = self._blockchain_util.call_contract_function(token_stake_contract, "stakeMap",
                                                                         [stake_index])
        return stake_window_data

    def _get_stake_holder_for_given_stake_index_and_address(self, stake_index, staker):
        token_stake_contract = self._get_token_stake_contract()
        stake_holder_data = self._blockchain_util.call_contract_function(
            token_stake_contract, "getStakeInfo", [stake_index, staker])
        return stake_holder_data

    def _add_stake_transaction(self, block_no, blockchain_id, transaction_hash, event_name, event_data, staker):
        transaction_date_in_epoch = self._blockchain_util.get_created_at_for_block(block_no=block_no). \
            get("timestamp", None)
        if transaction_date_in_epoch is not None:
            transaction_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(transaction_date_in_epoch))
        stake_transaction = StakeTransaction(
            blockchain_id=blockchain_id, transaction_hash=transaction_hash, event=event_name, event_data=event_data,
            block_no=block_no, transaction_date=transaction_date, staker=staker)
        stake_transaction_repo.add_stake_transaction(stake_transaction)


# {'stakeIndex': 1, 'tokenOperator': '0x', 'startPeriod': 1582910924, 'endPeriod': 1582996073, 'approvalEndPeriod': 1582918193, 'rewardAmount': 2500000000}

class OpenForStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"OpenForStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        stake_window_data = self._get_stake_window_by_stake_index(blockchain_id)
        logger.info(f"stake_window_data from blockchain for blockchain_id {blockchain_id}")
        start_period = stake_window_data[0]
        submission_end_period = stake_window_data[1]
        approval_end_period = stake_window_data[2]
        request_withdraw_start_period = stake_window_data[3]
        end_period = stake_window_data[4]
        min_stake = stake_window_data[5]
        max_stake = stake_window_data[6]
        window_max_cap = stake_window_data[7]
        open_for_external = stake_window_data[8]
        total_stake = stake_window_data[9]
        reward_amount = stake_window_data[9]
        stake_window = StakeWindow(
            blockchain_id=blockchain_id, start_period=start_period, submission_end_period=submission_end_period,
            approval_end_period=approval_end_period, request_withdraw_start_period=request_withdraw_start_period,
            end_period=end_period, min_stake=min_stake, max_stake=max_stake, window_max_cap=window_max_cap,
            open_for_external=open_for_external, total_stake=total_stake, reward_amount=reward_amount,
            token_operator=event_data["tokenOperator"])
        stake_window_repo.add_stake_window(stake_window)


# {'stakeIndex': 2, 'staker': '0x46EF7d49aaA68B29C227442BDbD18356415f8304', 'stakeAmount': 800000000, 'autoRenewal': True}
class SubmitStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"SubmitStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data[1]
        amount_approved = stake_holder_data[2]
        auto_renewal = stake_holder_data[3]
        block_no_created = event["data"]["block_no"]
        refund_amount = event_data["returnAmount"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created, refund_amount
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)
        self._add_stake_transaction(
            block_no=block_no_created, blockchain_id=blockchain_id, transaction_hash=event["data"]["transactionHash"],
            event_name=event["data"]["event"], event_data=event["data"], staker=staker)


# {'stakeIndex': 2, 'staker': '0x46EF7d49aaA68B29C227442BDbD18356415f8304', 'tokenOperator': '0x2e9c6C4145107cD21fCDc7319E4b24a8FF636c6B', 'approvedStakeAmount': 750000000, 'returnAmount': 0}
class ApproveStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"ApproveStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data[1]
        amount_approved = stake_holder_data[2]
        auto_renewal = stake_holder_data[3]
        block_no_created = event["data"]["block_no"]
        refund_amount = event_data["returnAmount"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created, refund_amount
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)
        self._add_stake_transaction(
            block_no=block_no_created, blockchain_id=blockchain_id, transaction_hash=event["data"]["transactionHash"],
            event_name=event["data"]["event"], event_data=event["data"], staker=staker)


class RejectStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"RejectStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data[1]
        amount_approved = stake_holder_data[2]
        auto_renewal = stake_holder_data[3]
        block_no_created = event["data"]["block_no"]
        refund_amount = event_data["returnAmount"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created, refund_amount
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)
        self._add_stake_transaction(
            block_no=block_no_created, blockchain_id=blockchain_id, transaction_hash=event["data"]["transactionHash"],
            event_name=event["data"]["event"], event_data=event["data"], staker=staker)


class WithdrawStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"WithdrawStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data[1]
        amount_approved = stake_holder_data[2]
        auto_renewal = stake_holder_data[3]
        block_no_created = event["data"]["block_no"]
        refund_amount = event_data["returnAmount"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created, refund_amount
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)
        self._add_stake_transaction(
            block_no=block_no_created, blockchain_id=blockchain_id, transaction_hash=event["data"]["transactionHash"],
            event_name=event["data"]["event"], event_data=event["data"], staker=staker)


# {'newStakeIndex': 4, 'staker': '0xC4f3BFE7D69461B7f363509393D44357c084404c', 'oldStakeIndex': 2, 'tokenOperator': '0x2e9c6C4145107cD21fCDc7319E4b24a8FF636c6B', 'stakeAmount': 3642553191, 'approvedAmount': 1700000000, 'returnAmount': 1942553191}
class AutoRenewTokenStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"WithdrawStake event data : {event_data}")
        staker = event_data["staker"]
        # update old stake holder record
        old_blockchain_id = event_data["oldStakeIndex"]
        old_stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(old_blockchain_id, staker)
        logger.info(
            f"old_stake_holder_data {old_stake_holder_data} from blockchain for given blockchain_id {old_blockchain_id} and staker {staker}")
        block_no_created = event["data"]["block_no"]
        refund_amount = event_data["returnAmount"]
        old_stake_holder = StakeHolder(
            old_blockchain_id, event_data["staker"], old_stake_holder_data[1],
            old_stake_holder_data[2], old_stake_holder_data[3], block_no_created, refund_amount
        )
        stake_holder_repo.add_or_update_stake_holder(old_stake_holder)
        self._add_stake_transaction(
            block_no=block_no_created, blockchain_id=old_blockchain_id, transaction_hash=event["data"]["transactionHash"],
            event_name=event["data"]["event"], event_data=event["data"], staker=staker)
        # update new stake holder record
        new_blockchain_id = event_data["newStakeIndex"]
        new_stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(new_blockchain_id, staker)
        logger.info(
            f"new_stake_holder_data {new_stake_holder_data} from blockchain for given blockchain_id {new_blockchain_id} and staker {staker}")
        block_no_created = event["data"]["block_no"]
        new_stake_holder = StakeHolder(
            new_blockchain_id, event_data["staker"], new_stake_holder_data[1],
            new_stake_holder_data[3], new_stake_holder_data[3], block_no_created, refund_amount
        )
        stake_holder_repo.add_or_update_stake_holder(new_stake_holder)
