import time
import math
from typing import Dict, Any, Union

from staking.config import TIME_INTERVAL_BETWEEN_CONSECUTIVE_STAKE_WINDOW, UPCOMING_STAKE_WINDOW_LIMIT
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
    def get_staker_count_for_given_window_id(window_id, last_window_id):
        if window_id == last_window_id:
            no_of_stakers = StakeHolderRepository().get_count_of_active_stakers()
        else:
            no_of_stakers = StakeHolderDetailsRepository().get_total_no_of_stakers(window_id)
        return no_of_stakers

    @staticmethod
    def get_all_stake_windows():
        stake_windows = StakeWindowRepository().get_stake_windows()
        list_of_stake_window = [stake_window.to_dict() for stake_window in stake_windows]
        last_stake_window = StakeWindowRepository().get_latest_stake_window()
        last_window_id = last_stake_window.blockchain_id
        for stake_window in list_of_stake_window:
            window_id = stake_window["window_id"]
            # Before Add Reward event total stake for current window will be 0
            # Total stake = new stake before the execution of Add Reward event
            if window_id == last_window_id and stake_window["total_stake"] == 0:
                stake_window["total_stake"] = StakeHolderRepository().get_total_amount_staked()
            stake_window.update({
                "no_of_stakers": StakeService.get_staker_count_for_given_window_id(window_id, last_window_id),
                "total_stake_deposited": stake_window["total_stake"]
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
        last_stake_window = StakeWindowRepository().get_latest_stake_window()
        last_window_id = last_stake_window.blockchain_id
        for transaction in stake_transactions:
            blockchain_id = transaction.blockchain_id
            if blockchain_id not in transactions_details.keys():
                stake_window = StakeWindowRepository().get_stake_window_for_given_blockchain_id(blockchain_id)
                no_of_stakers = StakeHolderDetailsRepository().get_unique_staker(blockchain_id)
                stake_window_dict = stake_window.to_dict()
                stake_window_dict.update({"no_of_stakers": no_of_stakers})
                if blockchain_id == last_window_id and not stake_window.total_stake:
                    total_stake = StakeHolderRepository().get_total_amount_staked()
                    stake_window_dict.update({"total_stake": total_stake})
                transactions_details[blockchain_id] = stake_window_dict
                transactions_details[blockchain_id]["transactions"] = []
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
        stake_holder_details = StakeHolderDetailsRepository().get_stake_holders_details_having_claimable_amount(
            staker=address)
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
        current_utc_time_in_epoch = time.time()
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
                active_stake_window = previous_stake_window
        if not active_stake_window:
            return active_stake_details
        stake_holder = StakeHolderRepository().get_stake_holder(staker=address)
        if not stake_holder:
            return active_stake_details
        active_window_id = active_stake_window.blockchain_id
        stake_holder_detail = StakeHolderDetailsRepository().get_stake_holder_details(blockchain_id=active_window_id,
                                                                                      staker=address)
        total_amount_staked = StakeHolderRepository().get_total_amount_staked()
        if stake_holder.amount_approved > 0 or stake_holder.amount_pending_for_approval > 0:
            pass
        else:
            return active_stake_details
        if active_stake_window.submission_end_period < current_utc_time_in_epoch < active_stake_window.request_withdraw_start_period:
            no_of_stakers = StakeHolderRepository().get_count_of_active_stakers()
        else:
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

    @staticmethod
    def get_upcoming_stake_windows_schedule():
        last_stake_window = StakeWindowRepository().get_latest_stake_window()
        if not last_stake_window:
            raise Exception("Unexpected behaviour.")
        current_window_id = last_stake_window.blockchain_id
        current_start_period = last_stake_window.start_period
        next_window_id, next_start_period = StakeService.get_upcoming_stake_window_schedule(
            current_window_id, current_start_period)
        upcoming_schedule = [{"window_id": current_window_id, "start_period": current_start_period,
                              "end_period": last_stake_window.end_period}]
        for i in range(0, UPCOMING_STAKE_WINDOW_LIMIT):
            upcoming_schedule.append({"window_id": next_window_id, "start_period": next_start_period})
            next_window_id, next_start_period = StakeService. \
                get_upcoming_stake_window_schedule(next_window_id, next_start_period)
        return upcoming_schedule

    @staticmethod
    def get_upcoming_stake_window_schedule(current_window_id, current_start_period):
        next_window_id = current_window_id + 1
        next_start_period = current_start_period + TIME_INTERVAL_BETWEEN_CONSECUTIVE_STAKE_WINDOW
        return next_window_id, next_start_period

    def get_stake_windows_schedule(self):
        current_stake_window = StakeWindowRepository().get_latest_stake_window()
        if not current_stake_window:
            raise Exception("Unexpected behaviour.")
        current_window_id = current_stake_window.blockchain_id
        current_start_period = current_stake_window.start_period

        # Past stake window details in descending order
        past_schedule = self.get_all_stake_windows()
        if past_schedule and past_schedule[0]["window_id"] == current_window_id:
            past_schedule.pop(0)
        # Current_stake_window
        current_schedule = current_stake_window.to_dict()

        # upcoming stake window_schedule in ascending order
        upcoming_schedule = []
        next_window_id, next_start_period = StakeService.get_upcoming_stake_window_schedule(
            current_window_id, current_start_period)
        for i in range(0, UPCOMING_STAKE_WINDOW_LIMIT):
            upcoming_schedule.append({"window_id": next_window_id, "start_period": next_start_period})
            next_window_id, next_start_period = StakeService. \
                get_upcoming_stake_window_schedule(next_window_id, next_start_period)
        return {
            "past": past_schedule,
            "upcoming": upcoming_schedule,
            "current": current_schedule
        }
