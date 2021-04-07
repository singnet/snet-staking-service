from datetime import datetime as dt

from sqlalchemy.exc import SQLAlchemyError

from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeHolder as StakeHolderDBModel
from staking.domain.factory.stake_factory import StakeFactory
from sqlalchemy import func, distinct, or_, and_
from common.logger import get_logger

logger = get_logger(__name__)


class StakeHolderRepository(BaseRepository):
    def get_stake_holder_balance(self, staker):
        try:
            staker_balance_db = self.session.query(StakeHolderDBModel).filter(StakeHolderDBModel.staker == staker).one()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        staker_balance = None
        if staker_balance_db is not None:
            staker_balance = StakeFactory.convert_stake_holder_db_model_to_entity_model(staker_balance_db)
        return staker_balance

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

