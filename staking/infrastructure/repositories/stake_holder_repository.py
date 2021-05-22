from datetime import datetime as dt

from sqlalchemy.exc import SQLAlchemyError

from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeHolder as StakeHolderDBModel
from staking.domain.factory.stake_factory import StakeFactory
from sqlalchemy import func, distinct, or_, and_
from common.logger import get_logger

logger = get_logger(__name__)


class StakeHolderRepository(BaseRepository):
    def get_stake_holder(self, staker):
        try:
            staker_holder_db = self.session.query(StakeHolderDBModel).filter(
                StakeHolderDBModel.staker == staker).first()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        staker_holder = None
        if staker_holder_db:
            staker_holder = StakeFactory.convert_stake_holder_db_model_to_entity_model(staker_holder_db)
        return staker_holder

    def add_or_update_stake_holder(self, stake_holder):
        staker = stake_holder.staker
        try:
            stake_holder_db = self.session.query(StakeHolderDBModel).filter(StakeHolderDBModel.staker == staker).first()
            if stake_holder_db:
                stake_holder_db.amount_pending_for_approval = stake_holder.amount_pending_for_approval
                stake_holder_db.amount_approved = stake_holder.amount_approved
                stake_holder_db.block_no_created = stake_holder.block_no_created
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        if not stake_holder_db:
            self.add_item(StakeHolderDBModel(
                staker=staker,
                amount_pending_for_approval=stake_holder.amount_pending_for_approval,
                amount_approved=stake_holder.amount_approved,
                block_no_created=stake_holder.block_no_created,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            ))
        return stake_holder

    def get_total_amount_staked(self):
        try:
            query_response = self.session.query(
                func.SUM(StakeHolderDBModel.amount_approved).label("total_amount_approved"),
                func.SUM(StakeHolderDBModel.amount_pending_for_approval).label(
                    "total_amount_pending_for_approval")).one()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        total_amount_approved = 0
        total_amount_pending_for_approval = 0
        if query_response.total_amount_approved or query_response.total_amount_pending_for_approval:
            total_amount_approved = int(query_response.total_amount_approved)
            total_amount_pending_for_approval = int(query_response.total_amount_pending_for_approval)
        total_amount_staked = total_amount_approved + total_amount_pending_for_approval
        return total_amount_staked

    def get_count_of_active_stakers(self):
        try:
            count_of_current_stakers = self.session.query(StakeHolderDBModel).filter(
                or_(StakeHolderDBModel.amount_approved > 0, StakeHolderDBModel.amount_pending_for_approval > 0)).count()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return count_of_current_stakers
