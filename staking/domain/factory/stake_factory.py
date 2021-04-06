from staking.domain.model.stake_window import StakeWindow
from staking.domain.model.stake_holder import StakeHolder
from staking.domain.model.stake_holder_details import StakeHolderDetails
from staking.domain.model.stake_transaction import StakeTransaction


class StakeFactory:
    def __init__(self):
        pass

    @staticmethod
    def convert_stake_window_db_model_to_entity_model(stake_window_db):
        return StakeWindow(
            blockchain_id=stake_window_db.blockchain_id,
            start_period=stake_window_db.start_period,
            submission_end_period=stake_window_db.submission_end_period,
            approval_end_period=stake_window_db.approval_end_period,
            request_withdraw_start_period=stake_window_db.request_withdraw_start_period,
            end_period=stake_window_db.end_period,
            min_stake=stake_window_db.min_stake,
            total_stake=stake_window_db.total_stake,
            open_for_external=stake_window_db.open_for_external,
            reward_amount=stake_window_db.reward_amount,
            token_operator=stake_window_db.token_operator
        )

    @staticmethod
    def convert_stake_holder_db_model_to_entity_model(stake_holder_db):
        return StakeHolder(
            staker=stake_holder_db.staker,
            amount_pending_for_approval=stake_holder_db.amount_pending_for_approval,
            amount_approved=stake_holder_db.amount_approved,
            block_no_created=stake_holder_db.block_no_created
        )

    @staticmethod
    def convert_stake_transaction_db_model_to_entity_model(stake_transaction_db):
        return StakeTransaction(
            blockchain_id=stake_transaction_db.blockchain_id,
            block_no=stake_transaction_db.block_no,
            event=stake_transaction_db.event,
            event_data=stake_transaction_db.event_data,
            transaction_hash=stake_transaction_db.transaction_hash,
            staker=stake_transaction_db.staker,
            transaction_date=stake_transaction_db.transaction_date
        )

    @staticmethod
    def convert_stake_holder_details_db_model_to_entity_model(stake_holder_details_db):
        return StakeHolderDetails(
            blockchain_id=stake_holder_details_db.blockchain_id,
            staker=stake_holder_details_db.staker,
            amount_staked=stake_holder_details_db.amount_staked,
            reward_amount=stake_holder_details_db.reward_amount,
            claimable_amount=stake_holder_details_db.claimable_amount,
            refund_amount=stake_holder_details_db.refund_amount,
            auto_renewal=stake_holder_details_db.auto_renewal,
            block_no_created=stake_holder_details_db.block_no_created
        )
