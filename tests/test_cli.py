# -*- coding: utf-8 -*-
from unittest import TestCase

from click.testing import CliRunner
from mock import patch

from frigg_worker.cli import start


class CLITests(TestCase):

    @patch('frigg_worker.cli.logger.info')
    @patch('frigg_worker.cli.fetch_builds')
    def test_start(self, mock_fetcher, mock_logger_info):
        runner = CliRunner()
        result = runner.invoke(start, ['builder'])
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once()
        mock_logger_info.assert_called_once_with('Starting frigg worker')

    @patch('frigg_worker.cli.logger.info')
    @patch('frigg_worker.cli.fetch_builds')
    def test_start_with_dispatcher_options(self, mock_fetcher, mock_logger_info):
        runner = CliRunner()
        result = runner.invoke(start, ['builder', '--dispatcher-url=http://frigg.io',
                                       '--dispatcher-token=to'])
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once()
        mock_logger_info.assert_called_once_with('Starting frigg worker')
        self.assertEqual(mock_fetcher.call_args_list[0][1]['dispatcher_token'], 'to')
        self.assertEqual(mock_fetcher.call_args_list[0][1]['dispatcher_url'], 'http://frigg.io')

    @patch('frigg_worker.cli.logger.info')
    @patch('frigg_worker.cli.fetch_builds')
    def test_start_with_hq_options(self, mock_fetcher, mock_logger_info):
        runner = CliRunner()
        result = runner.invoke(start, ['builder', '--hq-url=http://frigg.io', '--hq-token=to'])
        self.assertEqual(result.exit_code, 0)
        mock_logger_info.assert_called_once_with('Starting frigg worker')
        mock_fetcher.assert_called_once()
        self.assertEqual(mock_fetcher.call_args_list[0][1]['hq_token'], 'to')
        self.assertEqual(mock_fetcher.call_args_list[0][1]['hq_url'], 'http://frigg.io')

    @patch('frigg_worker.cli.logger.info')
    @patch('frigg_worker.cli.fetch_builds')
    def test_start_with_loglevel(self, mock_fetcher, mock_logger_info):
        runner = CliRunner()
        result = runner.invoke(start, ['builder', '--loglevel=ERROR'])
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once()
        mock_logger_info.assert_called_once_with('Starting frigg worker')
        self.assertEqual(mock_fetcher.call_args_list[0][1]['loglevel'], 'ERROR')

    @patch('frigg_worker.cli.logger.info')
    @patch('frigg_worker.cli.fetch_builds')
    def test_start_has_worker_host(self, mock_fetcher, mock_logger_info):
        runner = CliRunner()
        runner.invoke(start, ['builder'])
        self.assertIn('worker_host', mock_fetcher.call_args[1])

    @patch('frigg_worker.cli.logger.info')
    @patch('frigg_worker.cli.fetch_deployments')
    def test_start_deployer(self, mock_fetcher, mock_logger_info):
        runner = CliRunner()
        result = runner.invoke(start, ['deployer'])
        self.assertEqual(result.exit_code, 0)
        mock_fetcher.assert_called_once()
        mock_logger_info.assert_called_once_with('Starting frigg worker')
