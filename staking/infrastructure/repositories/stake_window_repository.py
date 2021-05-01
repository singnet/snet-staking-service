from datetime import datetime as dt

from sqlalchemy.exc import SQLAlchemyError

from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeWindow as StakeWindowDBModel
from staking.domain.factory.stake_factory import StakeFactory
from sqlalchemy import or_, func, desc
from staking.exceptions import StakeWindowNotFoundException


class StakeWindowRepository(BaseRepository):
    def get_total_reward_across_all_stake_window(self):
        try:
            query_response = self.session.query(
                func.sum(StakeWindowDBModel.reward_amount).label("total_reward_amount")).one()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        total_stake = int(query_response.total_reward_amount)
        return total_stake

    def get_total_stake_across_all_stake_window(self):
        try:
            query_response = self.session.query(func.sum(StakeWindowDBModel.total_stake).label("total_stake")).one()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        total_stake = int(query_response.total_stake)
        return total_stake

    def get_stake_windows(self):
        # Get all stake windows for which stake approval should be done or started.
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        try:
            stake_windows_raw_data = self.session.query(StakeWindowDBModel). \
                filter(StakeWindowDBModel.submission_end_period <= current_time). \
                order_by(StakeWindowDBModel.blockchain_id.desc()).all()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        stake_windows = [StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
                         for stake_window_db in stake_windows_raw_data]
        return stake_windows

    def get_latest_stake_window(self):
        try:
            stake_window_db = self.session.query(StakeWindowDBModel).order_by(
                StakeWindowDBModel.blockchain_id.desc()).first()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        stake_window = None
        if stake_window_db is not None:
            stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
        return stake_window

    def get_stake_window_for_given_blockchain_id(self, blockchain_id):
        try:
            stake_window_db = self.session.query(StakeWindowDBModel).filter(
                StakeWindowDBModel.blockchain_id == blockchain_id) \
                .one()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        stake_window = None
        if stake_window_db:
            stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
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
            open_for_external=stake_window.open_for_external,
            total_stake=stake_window.total_stake,
            reward_amount=stake_window.reward_amount,
            token_operator=stake_window.token_operator,
            created_on=dt.utcnow(),
            updated_on=dt.utcnow()
        ))
        return stake_window

    def get_stake_window_open_for_submission(self):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        try:
            stake_window_db = self.session.query(StakeWindowDBModel).filter(
                StakeWindowDBModel.start_period <= current_time) \
                .filter(StakeWindowDBModel.submission_end_period >= current_time).first()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        stake_window = None
        if stake_window_db:
            stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
        return stake_window

    def get_upcoming_stake_window(self):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        try:
            stake_window_db = self.session.query(StakeWindowDBModel).filter(
                StakeWindowDBModel.start_period >= current_time).first()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        stake_window = None
        if stake_window_db:
            stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
        return stake_window

    def update_stake_window(self, stake_window):
        try:
            stake_window_db = self.session.query(
                StakeWindowDBModel).filter(StakeWindowDBModel.blockchain_id == stake_window.blockchain_id).one()
            if stake_window_db:
                stake_window_db.start_period = stake_window.start_period,
                stake_window_db.submission_end_period = stake_window.submission_end_period,
                stake_window_db.approval_end_period = stake_window.approval_end_period,
                stake_window_db.request_withdraw_start_period = stake_window.request_withdraw_start_period,
                stake_window_db.end_period = stake_window.end_period,
                stake_window_db.min_stake = stake_window.min_stake,
                stake_window_db.total_stake = stake_window.total_stake,
                stake_window_db.reward_amount = stake_window.reward_amount,
                stake_window_db.token_operator = stake_window.token_operator,
                stake_window_db.updated_on = dt.utcnow()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
        return stake_window
