class CustomException(Exception):

    def __init__(self, error_details):
        self.error_details = error_details


class BadRequestException(CustomException):
    error_message = "BAD_REQUEST"

    def __init__(self):
        super().__init__({})


class ActiveStakeWindowNotFound(CustomException):
    error_message = "ACTIVE_STAKE_WINDOW_NOT_FOUND"

    def __init__(self):
        super().__init__({})


class StakeWindowNotFound(CustomException):
    error_message = "STAKE_WINDOW_NOT_FOUND"

    def __init__(self):
        super().__init__({})


EXCEPTIONS = (BadRequestException, ActiveStakeWindowNotFound, StakeWindowNotFound)
