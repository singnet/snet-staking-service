import os
import time
import json
from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.utils import send_slack_notification
from staking.config import SLACK_HOOK
from staking.domain.model.stake_holder import StakeHolder
from staking.domain.model.stake_transaction import StakeTransaction
from staking.domain.model.stake_window import StakeWindow
from staking.domain.model.stake_holder_details import StakeHolderDetails
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_holder_details_repository import StakeHolderDetailsRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository

logger = get_logger(__name__)
stake_window_repo = StakeWindowRepository()
stake_holder_repo = StakeHolderRepository()
stake_holder_details_repo = StakeHolderDetailsRepository()
stake_transaction_repo = StakeTransactionRepository()


class TokenStakeEventConsumer(object):

    def __init__(self, ws_provider, net_id):
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self._net_id = net_id

    def on_event(self, event):
        pass

    def _get_token_stake_contract(self):
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'node_modules', 'singularitynet-stake-contracts'))
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


class OpenForStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"OpenForStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        stake_window_data = self._get_stake_window_by_stake_index(blockchain_id)
        logger.info(f"stake_window_data {stake_window_data} from blockchain for blockchain_id {blockchain_id}")
        start_period = stake_window_data[0]
        submission_end_period = stake_window_data[1]
        approval_end_period = stake_window_data[2]
        request_withdraw_start_period = stake_window_data[3]
        end_period = stake_window_data[4]
        min_stake = stake_window_data[5]
        open_for_external = stake_window_data[6]
        reward_amount = stake_window_data[7]
        token_operator = event_data["tokenOperator"]
        stake_window = StakeWindow(
            blockchain_id=blockchain_id, start_period=start_period, submission_end_period=submission_end_period,
            approval_end_period=approval_end_period, request_withdraw_start_period=request_withdraw_start_period,
            end_period=end_period, min_stake=min_stake, total_stake=0, open_for_external=open_for_external,
            reward_amount=reward_amount, token_operator=token_operator)
        stake_window_repo.add_stake_window(stake_window)


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
        if stake_holder_data[0]:
            amount_approved = stake_holder_data[1]
            amount_pending_for_approval = stake_holder_data[2]
            reward_computed_index = stake_holder_data[3]
            claimable_amount = stake_holder_data[4]
            block_no_created = event["data"]["block_no"]
            stake_holder = StakeHolder(staker, amount_pending_for_approval, amount_approved, block_no_created)
            stake_holder_repo.add_or_update_stake_holder(stake_holder)
            stake_holder_details = StakeHolderDetails(blockchain_id, staker, amount_staked=amount_approved,
                                                      reward_amount=0, claimable_amount=claimable_amount,
                                                      refund_amount=0, auto_renewal=True,
                                                      block_no_created=block_no_created)
            stake_holder_details_repo.add_or_update_stake_holder_details(stake_holder_details)
            self._add_stake_transaction(
                block_no=block_no_created, blockchain_id=blockchain_id,
                transaction_hash=event["data"]["transactionHash"],
                event_name=event["data"]["event"], event_data=event["data"], staker=staker)
        else:
            raise Exception(f"Record not found for given blockchain_id {blockchain_id} and staker {staker}")


class RequestForClaimEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"RequestForClaim event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and "
            f"staker {staker}")
        print(stake_holder_data)
        if stake_holder_data[0]:
            amount_approved = stake_holder_data[1]
            amount_pending_for_approval = stake_holder_data[2]
            reward_computed_index = stake_holder_data[3]
            claimable_amount = stake_holder_data[4]
            block_no_created = event["data"]["block_no"]
            # update stake holder details
            stake_holder = StakeHolder(staker, amount_pending_for_approval, amount_approved, block_no_created)
            stake_holder_repo.add_or_update_stake_holder(stake_holder)
            # update auto renewal
            stake_holder_details = stake_holder_details_repo.get_stake_holder_details(blockchain_id, staker)
            stake_holder_details.auto_renewal = event_data["autoRenewal"]
            stake_holder_details.claimable_amount = claimable_amount
            stake_holder_details_repo.add_or_update_stake_holder_details(stake_holder_details)
            logger.info(f"stake_holder_details: {stake_holder_details.to_dict()}")
            # update stake transactions
            self._add_stake_transaction(
                block_no=block_no_created, blockchain_id=blockchain_id,
                transaction_hash=event["data"]["transactionHash"],
                event_name=event["data"]["event"], event_data=event["data"], staker=staker)


class ClaimStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"ClaimStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and "
            f"staker {staker}")
        print(stake_holder_data)
        if stake_holder_data[0]:
            amount_approved = stake_holder_data[1]
            amount_pending_for_approval = stake_holder_data[2]
            reward_computed_index = stake_holder_data[3]
            block_no_created = event["data"]["block_no"]
            # update stake holder details
            stake_holder = StakeHolder(staker, amount_pending_for_approval, amount_approved, block_no_created)
            stake_holder_repo.add_or_update_stake_holder(stake_holder)
            # update auto renewal
            stake_holder_details = stake_holder_details_repo.get_stake_holder_details(blockchain_id, staker)
            stake_holder_details.claimable_amount = event_data["totalAmount"]
            stake_holder_details_repo.add_or_update_stake_holder_details(stake_holder_details)
            # update stake transactions
            self._add_stake_transaction(
                block_no=block_no_created, blockchain_id=blockchain_id,
                transaction_hash=event["data"]["transactionHash"],
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
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and "
            f"staker {staker}")
        print(stake_holder_data)
        if stake_holder_data[0]:
            amount_approved = stake_holder_data[1]
            amount_pending_for_approval = stake_holder_data[2]
            reward_computed_index = stake_holder_data[3]
            block_no_created = event["data"]["block_no"]
            # update stake holder details
            stake_holder = StakeHolder(staker, amount_pending_for_approval, amount_approved, block_no_created)
            stake_holder_repo.add_or_update_stake_holder(stake_holder)
            # update auto renewal
            stake_holder_details = stake_holder_details_repo.get_stake_holder_details(blockchain_id, staker)
            stake_holder_details.refund_amount = event_data["returnAmount"]
            stake_holder_details_repo.add_or_update_stake_holder_details(stake_holder_details)
            # update stake transactions
            self._add_stake_transaction(
                block_no=block_no_created, blockchain_id=blockchain_id,
                transaction_hash=event["data"]["transactionHash"],
                event_name=event["data"]["event"], event_data=event["data"], staker=staker)


class AddRewardEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider):
        super().__init__(net_id=net_id, ws_provider=ws_provider)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"AddReward event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and "
            f"staker {staker}")
        print(stake_holder_data)
        if stake_holder_data[0]:
            amount_approved = stake_holder_data[1]
            amount_pending_for_approval = stake_holder_data[2]
            reward_computed_index = stake_holder_data[3]
            claimable_amount = stake_holder_data[4]
            block_no_created = event["data"]["block_no"]
            # update stake holder details
            stake_holder = StakeHolder(staker, amount_pending_for_approval, amount_approved, block_no_created)
            stake_holder_repo.add_or_update_stake_holder(stake_holder)
            # update auto renewal
            stake_holder_details = stake_holder_details_repo.get_stake_holder_details(blockchain_id, staker)
            reward_amount = event_data["rewardAmount"]
            if stake_holder_details:
                stake_holder_details.reward_amount = reward_amount
            else:
                amount_staked = event_data["totalStakeAmount"] - event_data["rewardAmount"]
                auto_renewal = 0 if claimable_amount > 0 else 1
                stake_holder_details = StakeHolderDetails(blockchain_id, staker, amount_staked, reward_amount, claimable_amount, 0, auto_renewal, block_no_created)
            stake_holder_details = stake_holder_details_repo.add_or_update_stake_holder_details(stake_holder_details)
            logger.info(f"stake_holder_details: {stake_holder_details.to_dict()}")
            # update total stake
            stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(blockchain_id=blockchain_id)
            stake_window.total_stake = event_data["windowTotalStake"] - stake_window.reward_amount
            stake_window_repo.update_stake_window(stake_window=stake_window)
            # update stake transactions
            self._add_stake_transaction(
                block_no=block_no_created, blockchain_id=blockchain_id,
                transaction_hash=event["data"]["transactionHash"],
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
            f"stake_holder_data {stake_holder_data} from blockchain for given blockchain_id {blockchain_id} and "
            f"staker {staker}")
        print(stake_holder_data)
        if stake_holder_data[0]:
            amount_approved = stake_holder_data[1]
            amount_pending_for_approval = stake_holder_data[2]
            reward_computed_index = stake_holder_data[3]
            block_no_created = event["data"]["block_no"]
            # update stake holder details
            stake_holder = StakeHolder(staker, amount_pending_for_approval, amount_approved, block_no_created)
            stake_holder_repo.add_or_update_stake_holder(stake_holder)
            # update auto renewal
            stake_holder_details = stake_holder_details_repo.get_stake_holder_details(blockchain_id, staker)
            stake_holder_details.claimable_amount = 0
            stake_holder_details_repo.add_or_update_stake_holder_details(stake_holder_details)
            # update stake transactions
            self._add_stake_transaction(
                block_no=block_no_created, blockchain_id=blockchain_id,
                transaction_hash=event["data"]["transactionHash"],
                event_name=event["data"]["event"], event_data=event["data"], staker=staker)
