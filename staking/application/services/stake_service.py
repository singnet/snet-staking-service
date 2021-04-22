import time
import math
from typing import Dict, Any, Union

from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_holder_details_repository import StakeHolderDetailsRepository
from staking.infrastructure.repositories.stake_transaction_respository import StakeTransactionRepository
from staking.exceptions import ActiveStakeWindowNotFoundException, StakeWindowNotFoundException
from common.logger import get_logger

logger = get_logger(__name__)


# window_total_stake = SUM(amount_approved + pending)
# Stake Window Table
#

class StakeService:
    def __init__(self):
        pass

    @staticmethod
    def get_stake_summary():
        total_reward = StakeWindowRepository().get_total_reward_across_all_stake_window()
        total_stake = StakeWindowRepository().get_total_stake_across_all_stake_window()
        no_of_unique_stakers = StakeHolderDetailsRepository().get_unique_staker()
        return {
            "no_of_stakers": no_of_unique_stakers,
            "total_reward": total_reward,
            "total_stake_deposited": total_stake
        }

    @staticmethod
    def get_all_stake_windows():
        stake_windows = StakeWindowRepository().get_stake_windows()
        list_of_stake_window = [stake_window.to_dict() for stake_window in stake_windows]
        for stake_window in list_of_stake_window:
            stake_window.update({
                "no_of_stakers": StakeHolderDetailsRepository().get_total_no_of_stakers(stake_window["blockchain_id"]),
                "total_stake_deposited": StakeHolderDetailsRepository().get_total_stake_deposited(
                    stake_window["blockchain_id"])

            })
        return list_of_stake_window

    @staticmethod
    def compute_auto_renewal_for_stake_window(blockchain_id):
        if blockchain_id < 1 or blockchain_id == 1:
            return 0
        stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(blockchain_id - 1)
        if stake_window is None or (not bool(stake_window.total_stake)):
            return 0
        total_auto_renew_amount = StakeHolderDetailsRepository().get_auto_renew_amount_for_given_stake_window(
            blockchain_id=blockchain_id)
        return total_auto_renew_amount

    @staticmethod
    def compute_auto_renewal_for_staker(blockchain_id, staker):
        if blockchain_id < 1 or blockchain_id == 1:
            return 0
        auto_renew_amount_for_staker = StakeHolderDetailsRepository().get_auto_renew_amount_for_given_stake_window(
            blockchain_id=blockchain_id, staker=staker)
        return auto_renew_amount_for_staker

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
        stake_holder = StakeHolderRepository().get_stake_holder(staker=staker)
        for stake_window in list_of_stake_window:
            blockchain_id = stake_window["blockchain_id"]
            no_of_stakers = StakeHolderDetailsRepository().get_unique_staker(blockchain_id=blockchain_id)
            # pending_stake_amount_for_staker = stake_holder.amount_pending_for_approval
            # approved_stake_amount_for_staker = stake_holder.amount_approved
            total_stake_deposited = StakeHolderDetailsRepository().get_total_stake_deposited(
                blockchain_id=blockchain_id)
            total_auto_renew_amount = StakeService.compute_auto_renewal_for_stake_window(blockchain_id=blockchain_id)
            auto_renew_amount_for_staker = \
                StakeService.compute_auto_renewal_for_staker(blockchain_id=blockchain_id, staker=staker)

            stake_window.update({
                "no_of_stakers": no_of_stakers,
                "total_stake_deposited": total_stake_deposited,
                "auto_renew_amount_for_staker": auto_renew_amount_for_staker,
                "total_auto_renew_amount": total_auto_renew_amount,

            })
        return {
            "stake_holder": stake_holder.to_dict(),
            "stake_windows": list_of_stake_window
        }

    @staticmethod
    def get_all_transactions_of_stake_holder_for_given_address(address):
        transactions_details = {}
        stake_transactions = StakeTransactionRepository().get_all_transactions_of_stake_holder_for_given_address(
            address)
        for transaction in stake_transactions:
            blockchain_id = transaction.blockchain_id
            if transactions_details.get(blockchain_id, None) is None:
                stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(blockchain_id)
                if stake_window is None:
                    stake_window_dict = {}
                else:
                    no_of_stakers = StakeHolderDetailsRepository().get_total_no_of_stakers(stake_window.blockchain_id)
                total_stake_deposited = stake_window.total_stake
                stake_window_dict = stake_window.to_dict()
                stake_window_dict.update(
                    {"no_of_stakers": no_of_stakers, "total_stake_deposited": total_stake_deposited})
                transactions_details[blockchain_id] = {
                    "stake_window": stake_window_dict,
                    "transactions": []
                }
            transactions_details[blockchain_id]["transactions"].append(transaction.to_dict())
        return list(transactions_details.values())

    @staticmethod
    def get_stake_holder_details_for_claim_stake_windows(address):
        claims_details = []
        # current_utc_time_in_epoch = time.time()
        # stake_holders = StakeHolderRepository().get_stake_holder_balance(address)
        # for stake_holder in stake_holders:
        #     blockchain_id = stake_holder.blockchain_id
        #     stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(blockchain_id)
        #     if not stake_window:
        #         raise StakeWindowNotFoundException()
        #     if (stake_holder.amount_approved > 0 and stake_window.end_period < current_utc_time_in_epoch) or (
        #             stake_holder.amount_pending_for_approval > 0 and stake_window.approval_end_period < current_utc_time_in_epoch):
        #         no_of_stakers = StakeHolderRepository().get_total_no_of_stakers(blockchain_id)
        #         total_stake_deposited = StakeHolderRepository().get_total_stake_deposited(blockchain_id)
        #         stake_window_dict = stake_window.to_dict()
        #         stake_window_dict.update(
        #             {"no_of_stakers": no_of_stakers, "total_stake_deposited": total_stake_deposited})
        #         claims_details.append({
        #             "stake_holder": stake_holder.to_dict(),
        #             "stake_window": stake_window_dict
        #         })
        return claims_details

    @staticmethod
    def get_stake_holder_details_for_active_stake_window(address):
        active_stake_details = []
        # current_utc_time_in_epoch = time.time()
        # stake_holders = StakeHolderRepository().get_stake_holders_for_given_address(address)
        # for stake_holder in stake_holders:
        #     blockchain_id = stake_holder.blockchain_id
        #     stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(blockchain_id)
        #     if not stake_window:
        #         raise StakeWindowNotFoundException()
        #     if (stake_holder.amount_approved > 0 and (
        #             stake_window.submission_end_period < current_utc_time_in_epoch < stake_window.end_period)
        #     ) or (stake_holder.amount_pending_for_approval > 0
        #           and (stake_window.approval_end_period > current_utc_time_in_epoch >
        #                stake_window.submission_end_period)):
        #         no_of_stakers = StakeHolderRepository().get_total_no_of_stakers(blockchain_id)
        #         total_stake_deposited = StakeHolderRepository().get_total_stake_deposited(blockchain_id)
        #         stake_window_dict = stake_window.to_dict()
        #         stake_window_dict.update(
        #             {"no_of_stakers": no_of_stakers, "total_stake_deposited": total_stake_deposited})
        #         active_stake_details.append({
        #             "stake_holder": stake_holder.to_dict(),
        #             "stake_window": stake_window_dict
        #         })
        return active_stake_details

    @staticmethod
    def get_stake_calculator_details():
        latest_stake_window = StakeWindowRepository().get_latest_stake_window()
        blockchain_id = latest_stake_window.blockchain_id

        total_stake_approved = latest_stake_window.total_stake
        total_stake_pending_for_approval = StakeHolderDetailsRepository().get_total_stake_deposited(
            blockchain_id=blockchain_id)

        total_auto_renew_amount = StakeService.compute_auto_renewal_for_stake_window(blockchain_id=blockchain_id)
        stake_calculator_details: Dict[Union[str, Any], Any] = latest_stake_window.to_dict()

        stake_calculator_details.update({
            "total_stake_pending_for_approval": total_stake_pending_for_approval,
            "total_stake_approved": total_stake_approved,
            "total_auto_renew_amount": total_auto_renew_amount
        })
        return stake_calculator_details
