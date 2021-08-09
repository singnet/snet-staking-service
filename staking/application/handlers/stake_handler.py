from common.utils import generate_lambda_response
from staking.config import SLACK_HOOK, NETWORK_ID
from common.logger import get_logger
from common.constant import StatusCode
from staking.exceptions import BadRequestException
from common.exception_handler import exception_handler
from staking.application.services.stake_service import StakeService

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_stake_summary(event, context):
    response = StakeService.get_stake_summary()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_all_stake_windows(event, context):
    response = StakeService.get_all_stake_windows()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_stake_window(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_parameters = event["queryStringParameters"]
    if "status" not in query_parameters or "staker" not in query_parameters:
        raise BadRequestException()
    response = StakeService.get_stake_window_based_on_status(status=query_parameters["status"],
                                                             staker=query_parameters["staker"])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_stake_holder_details_for_active_stake_window(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_parameters = event["queryStringParameters"]
    if "address" not in query_parameters:
        raise BadRequestException()
    response = StakeService.get_stake_holder_details_for_active_stake_window(address=query_parameters["address"])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_stake_holder_details_for_claim_stake_windows(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_parameters = event["queryStringParameters"]
    if "address" not in query_parameters:
        raise BadRequestException()
    response = StakeService.get_stake_holder_details_for_claim_stake_windows(address=query_parameters["address"])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_all_transactions_of_stake_holder_for_given_address(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_parameters = event["queryStringParameters"]
    if "address" not in query_parameters:
        raise BadRequestException()
    response = StakeService.get_all_transactions_of_stake_holder_for_given_address(address=query_parameters["address"])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_stake_calculator_details(event, context):
    response = StakeService.get_stake_calculator_details()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_upcoming_stake_windows_schedule(event, context):
    response = StakeService.get_upcoming_stake_windows_schedule()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_stake_windows_schedule(event, context):
    response = StakeService().get_stake_windows_schedule()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )