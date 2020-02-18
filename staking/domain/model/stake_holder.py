class StakeHolder:
    def __init__(self, blockchain_id, staker, amount, amount_staked, amount_pending_for_approval, amount_approved,
                 auto_renewal, status, staker_id, block_no_created):
        self._blockchain_id = blockchain_id
        self._staker = staker
        self._amount = amount
        self._amount_staked = amount_staked
        self._amount_pending_for_approval = amount_pending_for_approval
        self._amount_approved = amount_approved
        self._auto_renewal = auto_renewal
        self._status = status
        self._staker_id = staker_id
        self._block_no_created = block_no_created

    def to_dict(self):
        return {
            "blockchain_id": self._blockchain_id,
            "staker": self._staker,
            "amount": self._amount,
            "amount_staked": self._amount_staked,
            "amount_pending_for_approval": self._amount_pending_for_approval,
            "amount_approved": self._amount_approved,
            "auto_renewal": self._auto_renewal,
            "status": self._status,
            "staker_id": self._staker_id,
            "block_no_created": self._block_no_created
        }

    @property
    def blockchain_id(self):
        return self._blockchain_id

    @property
    def staker(self):
        return self._staker

    @property
    def amount(self):
        return self._amount

    @property
    def amount_staked(self):
        return self._amount_staked

    @property
    def amount_pending_for_approval(self):
        return self._amount_pending_for_approval

    @property
    def amount_approved(self):
        return self._amount_approved

    @property
    def auto_renewal(self):
        return self._auto_renewal

    @property
    def status(self):
        return self._status

    @property
    def staker_id(self):
        return self._staker_id

    @property
    def block_no_created(self):
        return self._block_no_created
