from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeHolder
from staking.domain.factory.stake_factory import StakeFactory
from sqlalchemy import func


class StakeHolderRepository(BaseRepository):
    def get_stake_holder_for_given_blockchain_index_and_address(self, blockchain_id, address):
        stake_holder_raw_data = self.session.query(StakeHolder).filter(StakeHolder.blockchain_id == blockchain_id) \
            .filter(StakeHolder.staker == address).all()
        stake_holders = [StakeFactory.convert_stake_holder_db_model_to_entity_model(stake_holder_db) for stake_holder_db
                         in stake_holder_raw_data]
        self.session.commit()
        return stake_holders

    def get_stake_holders_for_given_address(self, address):
        stake_holder_raw_data = self.session.query(StakeHolder).filter(StakeHolder.staker == address).all()
        stake_holders = [StakeFactory.convert_stake_holder_db_model_to_entity_model(stake_holder_db) for stake_holder_db
                         in stake_holder_raw_data]
        self.session.commit()
        return stake_holders

    def get_total_no_of_stakers(self, blockchain_id):
        total_no_of_stakers = self.session.query(StakeHolder).filter(StakeHolder.blockchain_id == blockchain_id).count()
        return total_no_of_stakers

    def get_total_stake_deposited(self, blockchain_id):
        total_stake_deposited = self.session.query(
            func.sum(StakeHolder.amount_pending_for_approval).label("total_stake_deposited")).filter(
            StakeHolder.blockchain_id == blockchain_id).all()
        return int(total_stake_deposited[0].total_stake_deposited)
