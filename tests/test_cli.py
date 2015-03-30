# -*- coding: utf-8 -*-
import sys
from io import StringIO
from unittest import TestCase

from click.testing import CliRunner
from mock import patch

from frigg_worker.cli import load_logging_config, start


class CLITestCase(TestCase):

    @patch('frigg_worker.cli.fetcher')
    def test_start(self, mock_fetcher):
        runner = CliRunner()
        result = runner.invoke(start, [])
        self.assertTrue('Starting frigg worker' in result.output)
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once_with(dispatcher_token=None, dispatcher_url=None)

    @patch('frigg_worker.cli.fetcher')
    def test_start_with_dispatcher_options(self, mock_fetcher):
        runner = CliRunner()
        result = runner.invoke(start, ['--dispatcher-url=http://frigg.io', '--dispatcher-token=to'])
        self.assertTrue('Starting frigg worker' in result.output)
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once_with(
            dispatcher_token='to',
            dispatcher_url='http://frigg.io'
        )

    @patch('frigg_worker.cli.fetcher', side_effect=OSError('os-error'))
    def test_start_with_error(self, mock_fetcher):
        runner = CliRunner()
        result = runner.invoke(start, [])
        self.assertTrue(mock_fetcher.called)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Starting frigg worker' in result.output)
        self.assertTrue('frigg_worker.cli - ERROR - os-error' in result.output)


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
