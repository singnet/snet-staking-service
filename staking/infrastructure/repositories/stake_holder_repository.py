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

