# -*- coding: utf-8 -*-
import os
import sys
from io import StringIO
from unittest import TestCase

from frigg_worker.cli import Commands, load_logging_config
from mock import patch


class CommandsTestCase(TestCase):

    def setUp(self):
        self._stdout = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._stdout

    def test_unknown_command(self):
        Commands.unknown_command()
        self.assertEqual(sys.stdout.getvalue(), 'Unknown command\n')

    def test_supervisor_config(self):
        Commands.supervisor_config()
        output = sys.stdout.getvalue()
        self.assertTrue(os.getcwd() in output)

    @patch('frigg_worker.cli.fetcher')
    def test_start(self, mock_fetcher):
        Commands.start()
        self.assertTrue(mock_fetcher.called)


class LoggingConfigLoaderTestCase(TestCase):
    def setUp(self):
        self._stdout = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._stdout

    def test_load_logging_config(self):
        load_logging_config()

    @patch('os.path.join', lambda *x: 'non-existing-path')
    def test_load_logging_config_failure(self):
        load_logging_config()
        self.assertTrue('There is a problem with the logging config:\n' in sys.stdout.getvalue())
