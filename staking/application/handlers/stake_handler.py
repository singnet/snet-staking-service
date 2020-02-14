from common.utils import handle_exception_with_slack_notification, generate_lambda_response
from staking.config import SLACK_HOOK, NETWORK_ID
from common.logger import get_logger
from common.constant import StatusCode

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_stake_window_details(event, context):
    response = "OK"
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
