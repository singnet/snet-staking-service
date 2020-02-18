from datetime import datetime as dt
from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeWindow
from staking.domain.factory.stake_factory import StakeFactory
from staking.exceptions import StakeWindowNotFound


class StakeWindowRepository(BaseRepository):

    def get_stake_window_open_for_submission(self):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        stake_windows_raw_data = self.session.query(StakeWindow).filter(StakeWindow.start_period <= current_time) \
            .filter(StakeWindow.submission_end_period >= current_time).all()
        stake_windows = [StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
                         for stake_window_db in stake_windows_raw_data]
        self.session.commit()
        return stake_windows

    def get_active_stake_window(self):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        stake_windows_raw_data = self.session.query(StakeWindow).filter(StakeWindow.start_period < current_time) \
            .filter(StakeWindow.end_period > current_time).all()
        stake_windows = [StakeFactory.convert_stake_window_db_model_to_entity_model(stake_window_db)
                         for stake_window_db in stake_windows_raw_data]
        self.session.commit()
        return stake_windows

    def get_stake_windows_for_given_blockchain_id(self, blockchain_id):
        current_time = dt.utcnow().timestamp()  # GMT Epoch
        stake_windows_raw_data = self.session.query(StakeWindow).filter(StakeWindow.blockchain_id == blockchain_id) \
            .filter(StakeWindow.end_period < current_time).all()
        if len(stake_windows_raw_data) == 0:
            raise StakeWindowNotFound()
        stake_window = StakeFactory.convert_stake_window_db_model_to_entity_model(stake_windows_raw_data[0])
        self.session.commit()
        return stake_window
