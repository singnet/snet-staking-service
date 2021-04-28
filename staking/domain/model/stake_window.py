class StakeWindow:
    def __init__(self, blockchain_id, start_period, submission_end_period, approval_end_period,
                 request_withdraw_start_period, end_period, min_stake, total_stake, open_for_external, reward_amount,
                 token_operator):
        self._blockchain_id = blockchain_id
        self._start_period = start_period
        self._submission_end_period = submission_end_period
        self._approval_end_period = approval_end_period
        self._request_withdraw_start_period = request_withdraw_start_period
        self._end_period = end_period
        self._min_stake = min_stake
        self._total_stake = total_stake
        self._open_for_external = open_for_external
        self._reward_amount = reward_amount
        self._token_operator = token_operator

    def to_dict(self):
        return {
            "blockchain_id": self._blockchain_id,
            "start_period": self._start_period,
            "submission_end_period": self._submission_end_period,
            "approval_end_period": self._approval_end_period,
            "request_withdraw_start_period": self._request_withdraw_start_period,
            "end_period": self._end_period,
            "min_stake": self._min_stake,
            "total_stake": self._total_stake,
            "open_for_external": self._open_for_external,
            "reward_amount": self._reward_amount,
            "token_operator": self._token_operator
        }

    @property
    def blockchain_id(self):
        return self._blockchain_id

    @property
    def start_period(self):
        return self._start_period

    @property
    def submission_end_period(self):
        return self._submission_end_period

    @property
    def approval_end_period(self):
        return self._approval_end_period

    @property
    def request_withdraw_start_period(self):
        return self._request_withdraw_start_period

    @property
    def end_period(self):
        return self._end_period

    @property
    def min_stake(self):
        return self._min_stake

    @property
    def total_stake(self):
        return self._total_stake

    @total_stake.setter
    def total_stake(self, total_stake):
        self._total_stake = total_stake

    @property
    def open_for_external(self):
        return self._open_for_external

    @property
    def reward_amount(self):
        return self._reward_amount

    @property
    def token_operator(self):
        return self._token_operator
