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
                "no_of_stakers": StakeHolderDetailsRepository().get_total_no_of_stakers(stake_window["window_id"]),
                # fix for last stake window
                "total_stake_deposited": StakeHolderDetailsRepository().get_total_stake_deposited(stake_window["blockchain_id"])
            })
        return list_of_stake_window

    @staticmethod
    def get_stake_window_based_on_status(status, staker):
        stake_window_details = {}
        if status == "OPEN":
            stake_window = StakeWindowRepository().get_stake_window_open_for_submission()
        if not stake_window:
            stake_window = StakeWindowRepository().get_upcoming_stake_window()
        if not stake_window:
            return stake_window_details
        stake_holder = StakeHolderRepository().get_stake_holder(staker=staker)
        no_of_stakers = StakeHolderRepository().get_count_of_active_stakers()
        total_amount_staked = StakeHolderRepository().get_total_amount_staked()
        stake_window_details = stake_window.to_dict()
        if stake_holder:
            stake_window_details.update(stake_holder.to_dict())
        stake_window_details.update({"no_of_stakers": no_of_stakers, "total_amount_staked": total_amount_staked})
        return stake_window_details

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
                    no_of_stakers = StakeHolderDetailsRepository().get_unique_staker(stake_window.blockchain_id)
                stake_window_dict = stake_window.to_dict()
                stake_window_dict.update({"no_of_stakers": no_of_stakers})
                transactions_details[blockchain_id] = {
                    "stake_window": stake_window_dict,
                    "transactions": []
                }
            transactions_details[blockchain_id]["transactions"].append(transaction.to_dict())
        return list(transactions_details.values())

    @staticmethod
    def get_stake_holder_details_for_claim_stake_windows(address):
        claims_details = []
        last_stake_window = StakeWindowRepository().get_latest_stake_window()
        last_window_id = last_stake_window.blockchain_id
        stake_holder = StakeHolderRepository().get_stake_holder(staker=address)
        if not stake_holder:
            return claims_details
        stake_holder_detail = StakeHolderDetailsRepository().get_stake_holder_details(last_window_id, address)
        if StakeService.is_stake_window_claimable(last_stake_window) and stake_holder.amount_approved > 0:
            no_of_stakers = StakeHolderDetailsRepository().get_unique_staker(last_window_id)
            claims_detail = last_stake_window.to_dict()
            claims_detail.update({"no_of_stakers": no_of_stakers})
            claims_detail.update(stake_holder.to_dict())
            if stake_holder_detail:
                claims_detail.update(stake_holder_detail.to_dict())
            claims_details.append(claims_detail)
        stake_holder_details = StakeHolderDetailsRepository().get_stake_holders_details_having_claimable_amount(staker=address)
        for stake_holder_detail in stake_holder_details:
            window_id = stake_holder_detail.blockchain_id
            stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(window_id)
            if StakeService.is_stake_window_claimable(stake_window):
                no_of_stakers = StakeHolderDetailsRepository().get_unique_staker(window_id)
                claims_detail = stake_window.to_dict()
                claims_detail.update({"no_of_stakers": no_of_stakers})
                claims_detail.update(stake_holder.to_dict())
                claims_detail.update(stake_holder_detail.to_dict())
                claims_details.append(claims_detail)
        return claims_details

    @staticmethod
    def is_stake_window_claimable(stake_window):
        current_utc_time_in_epoch = time.time()
        if stake_window.end_period < current_utc_time_in_epoch:
            return True
        else:
            return False

    @staticmethod
    def get_stake_holder_details_for_active_stake_window(address):
        active_stake_details = {}
        active_stake_window = None
        last_stake_window = StakeWindowRepository().get_latest_stake_window()
        last_window_id = last_stake_window.blockchain_id
        if StakeService.is_stake_window_active(last_stake_window):
            active_stake_window = last_stake_window
        elif last_window_id > 1:
            logger.info(f"Get previous stake window.")
            previous_blockchain_id = last_stake_window.blockchain_id - 1
            previous_stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(
                blockchain_id=previous_blockchain_id)
            if StakeService.is_stake_window_active(previous_stake_window):
                active_stake_window = last_stake_window
        if not active_stake_window:
            return active_stake_details
        stake_holder = StakeHolderRepository().get_stake_holder(staker=address)
        if not stake_holder:
            return active_stake_details
        active_window_id = active_stake_window.blockchain_id
        stake_holder_detail = StakeHolderDetailsRepository().get_stake_holder_details(blockchain_id=active_window_id,
                                                                                      staker=address)
        total_amount_staked = StakeHolderRepository().get_total_amount_staked()
        if active_window_id == last_window_id and (
                stake_holder.amount_approved > 0 or stake_holder.amount_pending_for_approval > 0):
            pass
        elif stake_holder_detail and active_window_id != last_window_id and stake_holder_detail.claimable_amount > 0:
            pass
        else:
            return active_stake_details
        no_of_stakers = StakeHolderDetailsRepository().get_unique_staker(active_window_id)
        active_stake_details = active_stake_window.to_dict()
        active_stake_details.update({"no_of_stakers": no_of_stakers})
        active_stake_details.update(stake_holder.to_dict())
        if stake_holder_detail:
            active_stake_details.update(stake_holder_detail.to_dict())
        active_stake_details.update({"total_amount_staked": total_amount_staked})
        return active_stake_details

    @staticmethod
    def is_stake_window_active(stake_window):
        current_utc_time_in_epoch = time.time()
        if stake_window.submission_end_period < current_utc_time_in_epoch < stake_window.end_period:
            return True
        else:
            return False

    @staticmethod
    def get_stake_calculator_details():
        last_stake_window = StakeWindowRepository().get_latest_stake_window()
        total_amount_staked = StakeHolderRepository().get_total_amount_staked()
        stake_calculator_details = last_stake_window.to_dict()
        stake_calculator_details.update({
            "total_amount_staked": total_amount_staked
        })
        return stake_calculator_details
