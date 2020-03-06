from datetime import datetime as dt
from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeTransaction as StakeTransactionDBModel
from staking.domain.factory.stake_factory import StakeFactory
from staking.domain.model.stake_transaction import StakeTransaction


class StakeTransactionRepository(BaseRepository):
    def get_all_transactions_of_stake_holder_for_given_address(self, address):
        transactions_raw_data = self.session.query(StakeTransactionDBModel).filter(
            StakeTransactionDBModel.staker == address). \
            order_by(StakeTransactionDBModel.blockchain_id.desc()). \
            order_by(StakeTransactionDBModel.block_no.desc()). \
            all()
        stake_transactions = [StakeFactory.convert_stake_transaction_db_model_to_entity_model(transaction) for
                              transaction in transactions_raw_data]
        return stake_transactions

    def add_stake_transaction(self, stake_transaction):
        self.add_item(
            StakeTransactionDBModel(
                blockchain_id=stake_transaction.blockchain_id,
                staker=stake_transaction.staker,
                event=stake_transaction.event,
                event_data=stake_transaction.event_data,
                block_no=stake_transaction.block_no,
                transaction_hash=stake_transaction.transaction_hash,
                transaction_date=stake_transaction.transaction_date,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
