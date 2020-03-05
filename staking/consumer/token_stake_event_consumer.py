from common.logger import get_logger
import os
import time
from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from staking.domain.model.stake_window import StakeWindow
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


# {'stakeIndex': 1, 'tokenOperator': '0x', 'startPeriod': 1582910924, 'endPeriod': 1582996073, 'approvalEndPeriod': 1582918193, 'rewardAmount': 2500000000}

class OpenForStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"OpenForStake event data : {event_data}")
        submission_end_period = 0
        request_withdraw_start_period = 0
        min_stake = 0
        max_stake = 0
        window_max_cap = 0
        open_for_external = 1
        total_stake = 0
        stake_window = StakeWindow(
            event_data["stakeIndex"], event_data["startPeriod"], submission_end_period,
            event_data["approval_end_period"], request_withdraw_start_period, event_data["end_period"], min_stake,
            max_stake, window_max_cap, open_for_external, total_stake, event_data["reward_amount"],
            event_data["token_operator"])
        stake_window_repo.add_stake_window(stake_window)


class SubmitStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"SubmitStake event data : {event_data}")


class ApproveStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"ApproveStake event data : {event_data}")


class RejectStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"RejectStake event data : {event_data}")


class WithdrawStakeEventConsumer(TokenStakeEventConsumer):

    def __init__(self, net_id, ws_provider, ipfs_url, ipfs_port):
        super().__init__(net_id, ws_provider, ipfs_url, ipfs_port)

    def on_event(self, event):
        event_data = self._get_event_data(event)
        logger.info(f"WithdrawStake event data : {event_data}")
