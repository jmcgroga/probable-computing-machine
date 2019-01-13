#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `zwift_pandas` package."""


import unittest
import getpass
import sys
from datetime import datetime, timedelta

import pandas as pd

from zwift_pandas import ZwiftDataFrame
from zwift_pandas import zwift_pandas

class TestZwift_pandas(unittest.TestCase):
    """Tests for `zwift_pandas` package."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures, if any."""
        username = getpass.getuser() + '@gmail.com'

        print()
        print('Username [%s]: ' % (username), end='', flush=True)
        cls.username = sys.stdin.readline().strip()

        if not cls.username:
            cls.username = username

        cls.password = getpass.getpass('Password: ')
        print('Player ID: ', end='', flush=True)
        cls.player_id = sys.stdin.readline().strip()

        print('Number of days: ', end='', flush=True)
        cls.num_days = int(sys.stdin.readline().strip()) - 1
        assert cls.num_days >= 0

        now = datetime.now()
        cls.start_date = now - timedelta(days=cls.num_days, hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond) 

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_generate_with_future_date(self):
        start_date = datetime(2099, 1, 1)
        count = 0
        for time, series in zwift_pandas.generate(self.username, self.password, self.player_id, start_date):
            count = 1
            break

        self.assertEqual(count, 0, 'Series returned when none expected')

    def test_generate_dataframe(self):
        df = zwift_pandas.ZwiftDataFrame(self.username, self.password, self.player_id, self.start_date)

        self.assertNotEqual(df.shape, (0, 0), 'Dataframe not generated')

        num_days = df.resample('D').mean().shape[0]

        self.assertNotEqual(num_days, self.num_days, 'Expected only %d days generated, %d were generated' % (self.num_days, num_days))

        
