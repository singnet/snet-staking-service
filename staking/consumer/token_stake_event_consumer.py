from common.logger import get_logger
import os
import time
from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from staking.domain.model.stake_window import StakeWindow
from staking.domain.model.stake_holder import StakeHolder
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository

logger = get_logger(__name__)
stake_window_repo = StakeWindowRepository()
stake_holder_repo = StakeHolderRepository()


class TokenStakeEventConsumer(object):

    def __init__(self, ws_provider, ipfs_url, ipfs_port, net_id):
        self._ipfs_util = IPFSUtil(ipfs_url, ipfs_port)
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

    def _get_token_stake_metadata_from_ipfs(self, ipfs_hash):
        return self._ipfs_util.read_file_from_ipfs(ipfs_hash)

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


# {'stakeIndex': 1, 'tokenOperator': '0x', 'startPeriod': 1582910924, 'endPeriod': 1582996073, 'approvalEndPeriod': 1582918193, 'rewardAmount': 2500000000}

class OpenForStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

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

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"SubmitStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(f"stake_holder_data from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data["pendingForApprovalAmount"]
        amount_approved = stake_holder_data["approvedAmount"]
        auto_renewal = stake_holder_data["autoRenewal"]
        block_no_created = event["block_no"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)


# {'stakeIndex': 2, 'staker': '0x46EF7d49aaA68B29C227442BDbD18356415f8304', 'tokenOperator': '0x2e9c6C4145107cD21fCDc7319E4b24a8FF636c6B', 'approvedStakeAmount': 750000000, 'returnAmount': 0}
class ApproveStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"ApproveStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(f"stake_holder_data from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data["pendingForApprovalAmount"]
        amount_approved = stake_holder_data["approvedAmount"]
        auto_renewal = stake_holder_data["autoRenewal"]
        block_no_created = event["block_no"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)


class RejectStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"RejectStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(f"stake_holder_data from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data["pendingForApprovalAmount"]
        amount_approved = stake_holder_data["approvedAmount"]
        auto_renewal = stake_holder_data["autoRenewal"]
        block_no_created = event["block_no"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)


class WithdrawStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"WithdrawStake event data : {event_data}")
        blockchain_id = event_data["stakeIndex"]
        staker = event_data["staker"]
        stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(blockchain_id, staker)
        logger.info(f"stake_holder_data from blockchain for given blockchain_id {blockchain_id} and staker {staker}")
        amount_pending_for_approval = stake_holder_data["pendingForApprovalAmount"]
        amount_approved = stake_holder_data["approvedAmount"]
        auto_renewal = stake_holder_data["autoRenewal"]
        block_no_created = event["block_no"]
        stake_holder = StakeHolder(
            blockchain_id, event_data["staker"], amount_pending_for_approval, amount_approved, auto_renewal,
            block_no_created
        )
        stake_holder_repo.add_or_update_stake_holder(stake_holder)


# {'newStakeIndex': 4, 'staker': '0xC4f3BFE7D69461B7f363509393D44357c084404c', 'oldStakeIndex': 2, 'tokenOperator': '0x2e9c6C4145107cD21fCDc7319E4b24a8FF636c6B', 'stakeAmount': 3642553191, 'approvedAmount': 1700000000, 'returnAmount': 1942553191}
class AutoRenewEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"WithdrawStake event data : {event_data}")
        staker = event_data["staker"]
        # update old stake holder record
        old_blockchain_id = event_data["oldStakeIndex"]
        old_stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(old_blockchain_id, staker)
        logger.info(
            f"old_stake_holder_data from blockchain for given blockchain_id {old_blockchain_id} and staker {staker}")
        block_no_created = event["block_no"]
        old_stake_holder = StakeHolder(
            old_blockchain_id, event_data["staker"], old_stake_holder_data["pendingForApprovalAmount"],
            old_stake_holder_data["approvedAmount"], old_stake_holder_data["autoRenewal"], block_no_created
        )
        stake_holder_repo.add_or_update_stake_holder(old_stake_holder)
        # update new stake holder record
        new_blockchain_id = event_data["newStakeIndex"]
        new_stake_holder_data = self._get_stake_holder_for_given_stake_index_and_address(new_blockchain_id, staker)
        logger.info(
            f"old_stake_holder_data from blockchain for given blockchain_id {new_blockchain_id} and staker {staker}")
        block_no_created = event["block_no"]
        new_stake_holder = StakeHolder(
            new_blockchain_id, event_data["staker"], new_stake_holder_data["pendingForApprovalAmount"],
            new_stake_holder_data["autoRenewal"], new_stake_holder_data["autoRenewal"], block_no_created
        )
        stake_holder_repo.add_or_update_stake_holder(new_stake_holder)
