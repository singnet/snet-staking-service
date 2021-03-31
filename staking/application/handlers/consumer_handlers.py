from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from staking.config import NETWORK, NETWORK_ID, SLACK_HOOK
from staking.consumer.token_stake_event_consumer import OpenForStakeEventConsumer, SubmitStakeEventConsumer, \
    ApproveStakeEventConsumer, RejectStakeEventConsumer, WithdrawStakeEventConsumer, AutoRenewStakeEventConsumer, \
    ClaimStakeEventConsumer, UpdateAutoRenewalEventConsumer, AddRewardEventConsumer
from staking.infrastructure.repositories.stake_holder_repository import StakeHolderRepository
from staking.infrastructure.repositories.stake_window_repository import StakeWindowRepository

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
    logger.info(f"Got SubmitStake Event {event}")
    SubmitStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


# @exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
# def approve_stake_consumer_handler(event, context):
#     logger.info(f"Got ApproveStake Event {event}")
#     ApproveStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
#         event)
#
#     return generate_lambda_response(200, StatusCode.OK)
#
#
# @exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
# def auto_renew_stake_consumer_handler(event, context):
#     logger.info(f"Got AutoRenewStake Event {event}")
#     AutoRenewStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
#         event)
#
#     return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def update_auto_renewal_consumer_handler(event, context):
    logger.info(f"Got UpdateAutoRenewal Event {event}")
    UpdateAutoRenewalEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def claim_stake_consumer_handler(event, context):
    logger.info(f"Got ClaimStake Event {event}")
    ClaimStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def reject_stake_consumer_handler(event, context):
    logger.info(f"Got RejectStake Event {event}")
    RejectStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def add_reward_consumer_handler(event, context):
    logger.info(f"Got AddReward Event {event}")
    AddRewardEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def withdraw_stake_consumer_handler(event, context):
    logger.info(f"Got WithdrawStake Event {event}")
    WithdrawStakeEventConsumer(net_id=NETWORK_ID, ws_provider=NETWORK['ws_provider']).on_event(
        event)

    return generate_lambda_response(200, StatusCode.OK)
