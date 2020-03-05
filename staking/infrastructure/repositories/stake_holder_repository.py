from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeHolder as StakeHolderDBModel
from staking.domain.factory.stake_factory import StakeFactory
from sqlalchemy import func


class StakeHolderRepository(BaseRepository):
    def get_stake_holder_for_given_blockchain_index_and_address(self, blockchain_id, address):
        stake_holder_raw_data = self.session.query(StakeHolderDBModel).filter(
            StakeHolderDBModel.blockchain_id == blockchain_id) \
            .filter(StakeHolderDBModel.staker == address).all()
        stake_holders = [StakeFactory.convert_stake_holder_db_model_to_entity_model(stake_holder_db) for stake_holder_db
                         in stake_holder_raw_data]
        self.session.commit()
        return stake_holders

    def get_stake_holders_for_given_address(self, address):
        stake_holder_raw_data = self.session.query(StakeHolderDBModel).filter(
            StakeHolderDBModel.staker == address).all()
        stake_holders = [StakeFactory.convert_stake_holder_db_model_to_entity_model(stake_holder_db) for stake_holder_db
                         in stake_holder_raw_data]
        self.session.commit()
        return stake_holders

    def get_total_no_of_stakers(self, blockchain_id):
        total_no_of_stakers = self.session.query(StakeHolderDBModel).filter(
            StakeHolderDBModel.blockchain_id == blockchain_id).count()
        self.session.commit()
        return total_no_of_stakers

    def get_total_stake_deposited(self, blockchain_id):
        total_stake_deposited = self.session.query(
            func.sum(StakeHolderDBModel.amount_pending_for_approval).label("total_stake_deposited")).filter(
            StakeHolderDBModel.blockchain_id == blockchain_id).all()
        self.session.commit()
        total_stake_deposit = total_stake_deposited[0].total_stake_deposited
        if total_stake_deposit is None:
            return 0
        return int(total_stake_deposit)

    def add_or_update_stake_holder(self, stake_holder):
        blockchain_id = stake_holder.blockchain_id
        staker = stake_holder.staker
        stake_holder_record = self.get_stake_holder_for_given_blockchain_index_and_address(
            blockchain_id=blockchain_id, address=staker)
        if not stake_holder_record:
            self.add_item(StakeHolderDBModel(
                blockchain_id=blockchain_id,
                staker=staker,
                amount_pending_for_approval=stake_holder.amount_pending_for_approval,
                amount_approved=stake_holder.amount_approved,
                auto_renewal=stake_holder.auto_renewal,
                block_no_created=stake_holder.block_no_created
            ))
        else:
            stake_holder_db = self.session.query(StakeHolderDBModel).\
                filter(StakeHolderDBModel.blockchain_id == blockchain_id).\
                filter(StakeHolderDBModel.staker == staker).all()
            stake_holder_db.amount_pending_for_approval = stake_holder.amount_pending_for_approval
            stake_holder_db.amount_approved = stake_holder.amount_approved
            stake_holder_db.auto_renewal = stake_holder.auto_renewal
            stake_holder_db.block_no_created = stake_holder.block_no_created
            self.session.commit()
        return stake_holder
