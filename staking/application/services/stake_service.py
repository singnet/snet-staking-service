from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository
from staking.exceptions import ActiveStakeWindowNotFound


class StakeService:
    def __init__(self):
        pass

    @staticmethod
    def get_stake_window_based_on_status(status, staker):
        stake_windows = []
        no_of_stakers = 0
        stake_amount_for_given_staker_address = 0
        total_stake_deposited_for_given_staker_address = 0
        if status == "OPEN":
            stake_windows = StakeWindowRepository().get_stake_window_open_for_submission()
        if not stake_windows:
            stake_windows = StakeWindowRepository().get_upcoming_stake_window()
        list_of_stake_window = [stake_window.to_dict() for stake_window in stake_windows]
        for stake_window in list_of_stake_window:
            stake_window.update({
                "no_of_stakers": StakeHolderRepository().get_total_no_of_stakers(stake_window["blockchain_id"]),
                "stake_amount_for_given_staker_address": sum(
                    [stake_holder.amount_pending_for_approval for stake_holder in
                     StakeHolderRepository().get_stake_holder_for_given_blockchain_index_and_address(
                         blockchain_id=stake_window["blockchain_id"],
                         address=staker)]),
                "total_stake_deposited": StakeHolderRepository().get_total_stake_deposited(
                    stake_window["blockchain_id"])

            })
        return list_of_stake_window

    @staticmethod
    def get_stake_holder_details_for_active_stake_window(address):
        # ACTIVE stake window means current time stamp is between stake window start period and end period
        stake_windows = StakeWindowRepository().get_active_stake_window()
        if len(stake_windows) == 0:
            return []
        response = []
        for stake_window in stake_windows:
            blockchain_id = stake_window.blockchain_id
            no_of_stakers = StakeHolderRepository().get_total_no_of_stakers(stake_window.blockchain_id)
            stake_window_dict = stake_window.to_dict()
            stake_window_dict.update({"no_of_stakers": no_of_stakers})
            stake_holder = StakeHolderRepository().get_stake_holder_for_given_blockchain_index_and_address(
                blockchain_id=blockchain_id, address=address)
            response.append({
                "stake_holder": stake_holder[0].to_dict() if len(stake_holder) > 0 else {},
                "stake_window": stake_window.to_dict()
            })
        return response

    @staticmethod
    def get_stake_holder_details_for_claim_stake_windows(address):
        claims_details = []
        stake_holders = StakeHolderRepository().get_stake_holders_for_given_address(address)
        for stake_holder in stake_holders:
            blockchain_id = stake_holder.blockchain_id
            stake_window = StakeWindowRepository().get_claim_stake_windows_for_given_blockchain_id(blockchain_id)
            if stake_window is None:
                stake_window_dict = {}
            else:
                no_of_stakers = StakeHolderRepository().get_total_no_of_stakers(stake_window.blockchain_id)
                stake_window_dict = stake_window.to_dict()
                stake_window_dict.update({"no_of_stakers": no_of_stakers})
            if stake_window is not None:
                claims_details.append({
                    "stake_holder": stake_holder.to_dict(),
                    "stake_window": stake_window_dict
                })
        return claims_details

    @staticmethod
    def get_all_transactions_of_stake_holder_for_given_address(address):
        transactions_details = []
        stake_transactions = StakeTransactionRepository().get_all_transactions_of_stake_holder_for_given_address(
            address)
        for transaction in stake_transactions:
            blockchain_id = transaction.blockchain_id
            stake_window = StakeWindowRepository().get_stake_windows_for_given_blockchain_id(blockchain_id)
            transactions_details.append({
                "transaction": transaction.to_dict(),
                "stake_window": stake_window.to_dict()
            })
        return transactions_details
