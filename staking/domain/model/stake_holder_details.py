class StakeHolderDetails:
    def __init__(self, blockchain_id, staker, amount_staked, reward_amount, claimable_amount, refund_amount,
                 auto_renewal, block_no_created):
        self.__blockchain_id = blockchain_id
        self.__staker = staker
        self.__amount_staked = amount_staked
        self.__reward_amount = reward_amount
        self.__claimable_amount = claimable_amount
        self.__refund_amount = refund_amount
        self.__auto_renewal = auto_renewal
        self.__block_no_created = block_no_created

    def to_dict(self):
        return {
            "blockchain_id": self.__blockchain_id,
            "staker": self.__staker,
            "amount_staked": self.__amount_staked,
            "reward_amount": self.__reward_amount,
            "claimable_amount": self.__claimable_amount,
            "refund_amount": self.__refund_amount,
            "auto_renewal": self.__auto_renewal,
            "block_no_created": self.__block_no_created
        }

    @property
    def blockchain_id(self):
        return self.__blockchain_id

    @property
    def staker(self):
        return self.__staker

    @property
    def amount_staked(self):
        return self.__amount_staked

    @amount_staked.setter
    def amount_staked(self, amount_staked):
        self.__amount_staked = amount_staked

    @property
    def reward_amount(self):
        return self.__reward_amount

    @reward_amount.setter
    def reward_amount(self, reward_amount):
        self.__reward_amount = reward_amount

    @property
    def claimable_amount(self):
        return self.__claimable_amount

    @claimable_amount.setter
    def claimable_amount(self, claimable_amount):
        self.__claimable_amount = claimable_amount

    @property
    def refund_amount(self):
        return self.__refund_amount

    @refund_amount.setter
    def refund_amount(self, refund_amount):
        self.__refund_amount = refund_amount

    @property
    def auto_renewal(self):
        return self.__auto_renewal

    @auto_renewal.setter
    def auto_renewal(self, auto_renewal):
        self.__auto_renewal = auto_renewal

    @property
    def block_no_created(self):
        return self.__block_no_created