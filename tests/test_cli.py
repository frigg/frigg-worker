# -*- coding: utf-8 -*-
from unittest import TestCase

from click.testing import CliRunner
from mock import patch

from frigg_worker.cli import start


class CLITestCase(TestCase):

    @patch('frigg_worker.cli.fetcher')
    def test_start(self, mock_fetcher):
        runner = CliRunner()
        result = runner.invoke(start, [])
        self.assertTrue('Starting frigg worker' in result.output)
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once()

    @patch('frigg_worker.cli.fetcher')
    def test_start_with_dispatcher_options(self, mock_fetcher):
        runner = CliRunner()
        result = runner.invoke(start, ['--dispatcher-url=http://frigg.io', '--dispatcher-token=to'])
        self.assertTrue('Starting frigg worker' in result.output)
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once()
        self.assertEqual(mock_fetcher.call_args_list[0][1]['dispatcher_token'], 'to')
        self.assertEqual(mock_fetcher.call_args_list[0][1]['dispatcher_url'], 'http://frigg.io')

    @patch('frigg_worker.cli.fetcher')
    def test_start_with_hq_options(self, mock_fetcher):
        runner = CliRunner()
        result = runner.invoke(start, ['--hq-url=http://frigg.io', '--hq-token=to'])
        self.assertTrue('Starting frigg worker' in result.output)
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once()
        self.assertEqual(mock_fetcher.call_args_list[0][1]['hq_token'], 'to')
        self.assertEqual(mock_fetcher.call_args_list[0][1]['hq_url'], 'http://frigg.io')

    @patch('frigg_worker.cli.fetcher', side_effect=OSError('os-error'))
    def test_start_with_error(self, mock_fetcher):
        runner = CliRunner()
        result = runner.invoke(start, [])
        self.assertTrue(mock_fetcher.called)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Starting frigg worker' in result.output)
        self.assertTrue('frigg_worker.cli - ERROR - os-error' in result.output)
