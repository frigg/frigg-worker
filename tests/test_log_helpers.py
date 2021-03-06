# -*- coding: utf-8 -*-
import sys
from io import StringIO
from unittest import TestCase

from frigg_worker.log_helpers import load_logging_config


class LoggingConfigLoaderTests(TestCase):
    def setUp(self):
        self._stdout = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._stdout

    def test_load_logging_config(self):
        config_dict = load_logging_config({'sentry_dsn': None, 'loglevel': 'DEBUG'})
        self.assertIn('formatters', config_dict)
        self.assertIn('handlers', config_dict)
        self.assertIn('loggers', config_dict)
        self.assertIn('', config_dict['loggers'])
        self.assertIn('requests', config_dict['loggers'])
        self.assertIn('frigg', config_dict['loggers'])
        self.assertIn('frigg_coverage', config_dict['loggers'])
        self.assertIn('frigg_worker', config_dict['loggers'])

    def test_load_config_custom_loglevel(self):
        config_dict = load_logging_config({'sentry_dsn': 'dsn', 'loglevel': 'CRITICAL'})
        self.assertEqual(config_dict['loggers']['frigg']['level'], 'CRITICAL')
