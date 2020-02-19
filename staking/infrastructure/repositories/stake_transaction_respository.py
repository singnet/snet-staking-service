from staking.infrastructure.repositories.base_repository import BaseRepository
from staking.infrastructure.models import StakeTransaction
from staking.domain.factory.stake_factory import StakeFactory


class StakeTransactionRepository(BaseRepository):
    def get_all_transactions_of_stake_holder_for_given_address(self, address):
        transactions_raw_data = self.session.query(StakeTransaction).filter(StakeTransaction.staker == address). \
            order_by(StakeTransaction.blockchain_id.desc()). \
            order_by(StakeTransaction.block_no.desc()). \
            all()
        stake_transactions = [StakeFactory.convert_stake_transaction_db_model_to_entity_model(transaction) for
                              transaction in transactions_raw_data]
        return stake_transactions
