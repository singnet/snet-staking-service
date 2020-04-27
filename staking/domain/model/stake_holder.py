class StakeHolder:
    def __init__(self, blockchain_id, staker, amount_pending_for_approval, amount_approved, auto_renewal,
                 block_no_created, refund_amount, new_staked_amount=None):
        self._blockchain_id = blockchain_id
        self._staker = staker
        self._amount_pending_for_approval = amount_pending_for_approval
        self._amount_approved = amount_approved
        self._auto_renewal = auto_renewal
        self._block_no_created = block_no_created
        self._refund_amount = refund_amount
        self._new_staked_amount = new_staked_amount

    def to_dict(self):
        return {
            "blockchain_id": self._blockchain_id,
            "staker": self._staker,
            "amount_pending_for_approval": self._amount_pending_for_approval,
            "amount_approved": self._amount_approved,
            "auto_renewal": self._auto_renewal,
            "block_no_created": self._block_no_created,
            "refund_amount": self._refund_amount
        }

    @property
    def blockchain_id(self):
        return self._blockchain_id

    @property
    def staker(self):
        return self._staker

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

    @property
    def refund_amount(self):
        return self._refund_amount

    @property
    def new_staked_amount(self):
        return self._new_staked_amount
