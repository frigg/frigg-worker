# -*- coding: utf-8 -*-
import sys
from io import StringIO
from unittest import TestCase

from frigg_worker.log_helpers import load_logging_config


class LoggingConfigLoaderTestCase(TestCase):
    def setUp(self):
        self._stdout = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._stdout

    def test_load_logging_config(self):
        config_dict = load_logging_config({'sentry_dsn': None})
        self.assertIn('formatters', config_dict)
        self.assertIn('handlers', config_dict)
        self.assertIn('loggers', config_dict)
        self.assertIn('', config_dict['loggers'])
        self.assertIn('requests', config_dict['loggers'])
        self.assertIn('frigg', config_dict['loggers'])
        self.assertIn('frigg_coverage', config_dict['loggers'])
        self.assertIn('frigg_worker', config_dict['loggers'])

        config_dict = load_logging_config({'sentry_dsn': 'dsn'})
        self.assertIn('sentry', config_dict['handlers'])
        self.assertEqual(config_dict['loggers']['frigg']['handlers'], ['console', 'sentry'])
