class StakeHolder:
    def __init__(self, staker, amount_pending_for_approval, amount_approved, block_no_created):
        self._staker = staker
        self._amount_pending_for_approval = amount_pending_for_approval
        self._amount_approved = amount_approved
        self._block_no_created = block_no_created

    def to_dict(self):
        return {
            "staker": self._staker,
            "amount_pending_for_approval": self._amount_pending_for_approval,
            "amount_approved": self._amount_approved,
            "block_no_created": self._block_no_created
        }

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
    def block_no_created(self):
        return self._block_no_created
