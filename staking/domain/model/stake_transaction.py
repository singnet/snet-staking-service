class StakeTransaction:
    def __init__(self, blockchain_id, transaction_hash, event, event_data, block_no, transaction_date, staker=None):
        self._blockchain_id = blockchain_id
        self._transaction_hash = transaction_hash
        self._event = event
        self._event_data = event_data
        self._block_no = block_no
        self._staker = staker
        self._transaction_date = transaction_date

    def to_dict(self):
        return {
            "blockchain_id": self._blockchain_id,
            "transaction_hash": self._transaction_hash,
            "event": self._event,
            "event_data": self._event_data,
            "block_no": self._block_no,
            "transaction_date": str(self._transaction_date),
        }

    @property
    def blockchain_id(self):
        return self._blockchain_id

    @property
    def transaction_hash(self):
        return self._transaction_hash

    @property
    def event(self):
        return self._event

    @property
    def event_data(self):
        return self._event_data

    @property
    def block_no(self):
        return self._block_no

    @property
    def staker(self):
        return self._staker

    @property
    def transaction_date(self):
        return self._transaction_date
