from datetime import datetime as dt
from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeWindow as StakeWindowDBModel
from staking.domain.factory.stake_factory import StakeFactory
from sqlalchemy import or_, func
from staking.exceptions import StakeWindowNotFoundException


class StakeWindowRepository(BaseRepository):

    def get_stake_windows(self):
        # Get all stake windows for which stake approval should be done or started.
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        stake_windows_raw_data = self.session.query(StakeWindowDBModel).\
            filter(StakeWindowDBModel.submission_end_period <= current_time). \
            order_by(StakeWindowDBModel.blockchain_id.desc()).all()
        stake_windows = [StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
                         for stake_window_db in stake_windows_raw_data]
        self.session.commit()
        return stake_windows

    def get_stake_window_open_for_submission(self):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        stake_windows_raw_data = self.session.query(StakeWindowDBModel).filter(
            StakeWindowDBModel.start_period <= current_time) \
            .filter(StakeWindowDBModel.submission_end_period >= current_time).all()
        stake_windows = [StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
                         for stake_window_db in stake_windows_raw_data]
        self.session.commit()
        return stake_windows

    def get_upcoming_stake_window(self):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        stake_windows_raw_data = self.session.query(StakeWindowDBModel).filter(
            StakeWindowDBModel.start_period >= current_time).all()
        stake_windows = [StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
                         for stake_window_db in stake_windows_raw_data]
        self.session.commit()
        return stake_windows

    def get_stake_window_for_given_blockchain_id(self, blockchain_id):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        stake_windows_raw_data = self.session.query(StakeWindowDBModel).filter(
            StakeWindowDBModel.blockchain_id == blockchain_id) \
            .all()
        if not bool(stake_windows_raw_data):
            self.session.commit()
            return None
        stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_windows_raw_data[0])
        self.session.commit()
        return stake_window

    def add_stake_window(self, stake_window):
        self.add_item(StakeWindowDBModel(
            blockchain_id=stake_window.blockchain_id,
            start_period=stake_window.start_period,
            submission_end_period=stake_window.submission_end_period,
            approval_end_period=stake_window.approval_end_period,
            request_withdraw_start_period=stake_window.request_withdraw_start_period,
            end_period=stake_window.end_period,
            min_stake=stake_window.min_stake,
            max_stake=stake_window.max_stake,
            window_max_cap=stake_window.window_max_cap,
            open_for_external=stake_window.open_for_external,
            total_stake=stake_window.total_stake,
            reward_amount=stake_window.reward_amount,
            token_operator=stake_window.token_operator,
            created_on=dt.utcnow(),
            updated_on=dt.utcnow()
        ))
        return stake_window

    def update_stake_window(self, stake_window):
        try:
            stake_windows_db = self.session.query(
                StakeWindowDBModel).filter(StakeWindowDBModel.blockchain_id == stake_window.blockchain_id).one()
            stake_windows_db.start_period = stake_window.start_period,
            stake_windows_db.submission_end_period = stake_window.submission_end_period,
            stake_windows_db.approval_end_period = stake_window.approval_end_period,
            stake_windows_db.request_withdraw_start_period = stake_window.request_withdraw_start_period,
            stake_windows_db.end_period = stake_window.end_period,
            stake_windows_db.min_stake = stake_window.min_stake,
            stake_windows_db.max_stake = stake_window.max_stake,
            stake_windows_db.window_max_cap = stake_window.window_max_cap,
            stake_windows_db.total_stake = stake_window.total_stake,
            stake_windows_db.reward_amount = stake_window.reward_amount,
            stake_windows_db.token_operator = stake_window.token_operator,
            stake_windows_db.updated_on = dt.utcnow()
            stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_windows_db)
            self.session.commit()
            return stake_window
        except Exception as e:
            self.session.rollback()
            raise e

    def get_total_reward_across_all_stake_window(self):
        query_response = self.session.query(
            func.sum(StakeWindowDBModel.reward_amount).label("total_reward_amount")).all()
        self.session.commit()
        total_reward_amount = query_response[0].total_reward_amount
        if total_reward_amount is None:
            return 0
        return int(total_reward_amount)
