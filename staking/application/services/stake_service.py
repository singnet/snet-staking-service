from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository
from staking.exceptions import ActiveStakeWindowNotFound


class StakeService:
    def __init__(self):
        pass

    @staticmethod
    def get_stake_window_based_on_status(status):
        stake_windows = []
        if status == "OPEN":
            stake_windows = StakeWindowRepository().get_stake_window_open_for_submission()
        return [stake_window.to_dict() for stake_window in stake_windows]

    @staticmethod
    def get_stake_holder_details_for_active_stake_window(address):
        # ACTIVE stake window means current time stamp is between stake window start period and end period
        stake_windows = StakeWindowRepository().get_active_stake_window()
        if len(stake_windows) == 0:
            raise ActiveStakeWindowNotFound()
        blockchain_id = stake_windows[0].blockchain_id
        stake_holders = StakeHolderRepository().get_stake_holder_for_given_blockchain_index_and_address(
            blockchain_id=blockchain_id, address=address)
        return {
            "stake_holder": stake_holders[0].to_dict(),
            "stake_window": stake_windows[0].to_dict()
        }

    @staticmethod
    def get_stake_holder_details_for_claim_stake_windows(address):
        claims_details = []
        stake_holders = StakeHolderRepository().get_stake_holders_for_given_address(address)
        for stake_holder in stake_holders:
            blockchain_id = stake_holder.blockchain_id
            stake_window = StakeWindowRepository().get_stake_windows_for_given_blockchain_id(blockchain_id)
            claims_details.append({
                "stake_holder": stake_holder.to_dict(),
                "stake_window": stake_window.to_dict()
            })
        return claims_details

    @staticmethod
    def get_all_transactions_of_stake_holder_for_given_address(address):
        stake_transactions = StakeTransactionRepository().get_all_transactions_of_stake_holder_for_given_address(
            address)
        return [transaction.to_dict() for transaction in stake_transactions]
