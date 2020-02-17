import unittest
from unittest import TestCase
from staking.application.handlers.stake_handler import get_stake_window_details


class TestStaking(TestCase):
    def setUp(self):
        pass

    def test_get_active_staking_window(self):
        event = {
            "httpMethod": "GET",
            "pathParameters": {},
            "queryStringParameters": {"status": "ACTIVE"}
        }
        response = get_stake_window_details(event=event, context=None)
