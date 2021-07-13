from common.constant import StatusCode
from common.logger import get_logger
from common.exception_handler import exception_handler
from common.utils import generate_lambda_response
from staking.config import SLACK_HOOK, NETWORK_ID
from staking.script.monitor_staking_data import MonitorStakingData

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def monitor_current_stake_window(event, context):
    MonitorStakingData().monitor_current_stake_window_details()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": {}, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def monitor_stake_for_staker(event, context):
    window_id = event["window_id"]
    staker = event["staker"]
    MonitorStakingData().monitor_stake_for_staker(window_id=window_id, staker=staker)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": {}, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def monitor_stake_for_all_stake_addresses(event, context):
    MonitorStakingData().monitor_stake_for_all_stake_addresses()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": {}, "error": {}}, cors_enabled=True
    )
