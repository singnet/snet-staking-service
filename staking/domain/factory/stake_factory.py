from staking.domain.model.stake_window import StakeWindow
from staking.domain.model.stake_holder import StakeHolder
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
            max_stake=stake_window_db.max_stake,
            window_max_cap=stake_window_db.window_max_cap,
            open_for_external=stake_window_db.open_for_external,
            total_stake=stake_window_db.total_stake,
            reward_amount=stake_window_db.reward_amount,
            token_operator=stake_window_db.token_operator
        )

    @staticmethod
    def convert_stake_holder_db_model_to_entity_model(stake_holder_db):
        return StakeHolder(
            blockchain_id=stake_holder_db.blockchain_id,
            staker=stake_holder_db.staker,
            amount=stake_holder_db.amount,
            amount_staked=stake_holder_db.amount_staked,
            amount_pending_for_approval=stake_holder_db.amount_pending_for_approval,
            amount_approved=stake_holder_db.amount_approved,
            auto_renewal=stake_holder_db.auto_renewal,
            status=stake_holder_db.status,
            staker_id=stake_holder_db.staker_id,
            block_no_created=stake_holder_db.block_no_created
        )

    @staticmethod
    def convert_stake_transaction_db_model_to_entity_model(stake_transaction_db):
        return StakeTransaction(
            transaction_id=stake_transaction_db.transaction_id,
            blockchain_id=stake_transaction_db.blockchain_id,
            block_no=stake_transaction_db.block_no,
            event=stake_transaction_db.event,
            event_data=stake_transaction_db.event_data,
            transaction_hash=stake_transaction_db.transaction_hash,
            staker=stake_transaction_db.staker
        )
