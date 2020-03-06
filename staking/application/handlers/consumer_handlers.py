from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from staking.config import NETWORK, NETWORK_ID, SLACK_HOOK
from staking.consumer.token_stake_event_consumer import OpenForStakeEventConsumer, SubmitStakeEventConsumer, \
    ApproveStakeEventConsumer, RejectStakeEventConsumer, WithdrawStakeEventConsumer, AutoRenewTokenStakeEventConsumer
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository

logger = get_logger(__name__)

stake_window_repo = StakeWindowRepository()
stake_holder_repo = StakeHolderRepository()


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def open_for_stake_consumer_handler(event, context):
    logger.info(f"Got OpenForStake Event {event}")
    OpenForStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def submit_stake_consumer_handler(event, context):
    logger.info(f"Got OpenForStake Event {event}")
    SubmitStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def approve_stake_consumer_handler(event, context):
    logger.info(f"Got OpenForStake Event {event}")
    ApproveStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def reject_stake_consumer_handler(event, context):
    logger.info(f"Got OpenForStake Event {event}")
    RejectStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def withdraw_stake_consumer_handler(event, context):
    logger.info(f"Got OpenForStake Event {event}")
    WithdrawStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def auto_renew_token_stake_consumer_handler(event, context):
    logger.info(f"Got OpenForStake Event {event}")
    AutoRenewTokenStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


