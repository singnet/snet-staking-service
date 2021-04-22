from datetime import datetime as dt
from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeHolderDetails as StakeHolderDetailsDBModel
from staking.domain.factory.stake_factory import StakeFactory
from sqlalchemy import func, distinct, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from common.logger import get_logger

logger = get_logger(__name__)


class StakeHolderDetailsRepository(BaseRepository):
    def get_stake_holder_details(self, blockchain_id, staker):
        try:
            stake_holder_details_db = self.session.query(StakeHolderDetailsDBModel).filter(
                StakeHolderDetailsDBModel.blockchain_id == blockchain_id) \
                .filter(StakeHolderDetailsDBModel.staker == staker).first()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        stake_holder_details = None
        if stake_holder_details_db:
            stake_holder_details = StakeFactory.convert_stake_holder_details_db_model_to_entity_model(
                stake_holder_details_db)
        return stake_holder_details

    def add_or_update_stake_holder_details(self, stake_holder_details):
        logger.info(f"add_or_update_stake_holder_details::stake_holder_details {stake_holder_details}")
        blockchain_id = stake_holder_details.blockchain_id
        staker = stake_holder_details.staker
        try:
            stake_holder_details_db = self.session.query(StakeHolderDetailsDBModel). \
                filter(StakeHolderDetailsDBModel.blockchain_id == blockchain_id). \
                filter(StakeHolderDetailsDBModel.staker == staker).first()
            if stake_holder_details_db:
                stake_holder_details_db.amount_staked = stake_holder_details.amount_staked
                stake_holder_details_db.reward_amount = stake_holder_details.reward_amount
                stake_holder_details_db.claimable_amount = stake_holder_details.claimable_amount
                stake_holder_details_db.refund_amount = stake_holder_details.refund_amount
                stake_holder_details_db.auto_renewal = stake_holder_details.auto_renewal
                stake_holder_details_db.block_no_created = stake_holder_details.block_no_created
                stake_holder_details_db.updated_on = dt.utcnow()
                stake_holder_details_db.block_no_created = stake_holder_details.block_no_created
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not stake_holder_details_db:
            self.add_item(StakeHolderDetailsDBModel(
                blockchain_id=blockchain_id,
                staker=staker,
                amount_staked=stake_holder_details.amount_staked,
                reward_amount=stake_holder_details.reward_amount,
                claimable_amount=stake_holder_details.claimable_amount,
                refund_amount=stake_holder_details.refund_amount,
                auto_renewal=stake_holder_details.auto_renewal,
                block_no_created=stake_holder_details.block_no_created,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        return stake_holder_details

    def get_unique_staker(self, blockchain_id=None):
        try:
            query = self.session.query(
                func.count(distinct(StakeHolderDetailsDBModel.staker)).label("no_of_unique_staker"))
            if blockchain_id is not None:
                query = query.filter(StakeHolderDetailsDBModel.blockchain_id == blockchain_id)
            query_response = query.one()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        no_of_unique_staker = int(query_response.no_of_unique_staker)
        return no_of_unique_staker

    def get_total_no_of_stakers(self, blockchain_id):
        try:
            total_no_of_stakers = self.session.query(StakeHolderDetailsDBModel).filter(
                StakeHolderDetailsDBModel.blockchain_id == blockchain_id).count()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return total_no_of_stakers

    def get_total_stake_deposited(self, blockchain_id):
        try:
            total_stake_deposited = self.session.query(
                func.sum(StakeHolderDetailsDBModel.amount_staked).label("amount_staked")).filter(
                StakeHolderDetailsDBModel.blockchain_id == blockchain_id).one()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return int(total_stake_deposited.amount_staked)

    def get_auto_renew_amount_for_given_stake_window(self, blockchain_id, staker=None):
        try:
            query = self.session.query(
                func.SUM(StakeHolderDetailsDBModel.amount_staked).label("principal_renewed"),
                func.SUM(StakeHolderDetailsDBModel.amount_staked).label("reward_renewed")). \
                filter(StakeHolderDetailsDBModel.blockchain_id < blockchain_id). \
                filter(StakeHolderDetailsDBModel.auto_renewal == 1)
            if staker is not None:
                query = query.filter(StakeHolderDetailsDBModel.staker == staker)
            query_response = query.one()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        auto_renew_amount = int(query_response.principal_renewed) + int(query_response.reward_renewed)
        return auto_renew_amount

    def get_total_no_of_stakers(self, blockchain_id):
        try:
            total_no_of_stakers = self.session.query(StakeHolderDetailsDBModel).filter(
                StakeHolderDetailsDBModel.blockchain_id == blockchain_id).count()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return total_no_of_stakers
