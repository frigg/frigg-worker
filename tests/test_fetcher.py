# -*- coding: utf-8 -*-
import json
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

import responses

from frigg_worker.fetcher import fetch_task, fetcher, start_build, start_deployment, upgrade

FETCH_OPTIONS = {
    'hq_url': None,
    'slack_url': None,
    'hq_token': None,
    'loglevel': 'DEBUG',
    'dispatcher_url': 'http://example.com',
    'slack_channel': '#workforce',
    'sentry_dsn': None,
    'dispatcher_token': None
}


class FetcherTests(TestCase):
    @patch('frigg_worker.fetcher.Docker')
    @patch('frigg_worker.builds.Build.run_tests')
    def test_start_build(self, mock_run_tests, mock_docker):
        start_build({
            'id': 1,
            'gh_token': 'a-token-one-might-say',
            'image': 'frigg/frigg-test-base'
        }, {
            'hq_token': 'test_token',
            'hq_url': 'url'
        })

        self.assertTrue(mock_run_tests.called)
        mock_docker.assert_called_once_with(
            privilege=True,
            combine_outputs=True,
            image='frigg/frigg-test-base',
            name_prefix='build',
            env_variables={'CI': 'frigg', 'GH_TOKEN': 'a-token-one-might-say'}
        )

    @patch('frigg_worker.fetcher.Docker')
    @patch('frigg_worker.deployments.Deployment.run_deploy')
    def test_start_deployment(self, mock_run_deploy, mock_docker):
        start_deployment({
            'id': 1,
            'gh_token': 'a-token-one-might-say',
            'image': 'frigg/frigg-test-base',
            'ttl': 1800,
            'port': 1440
        }, {
            'hq_token': 'test_token',
            'hq_url': 'url'
        })

        self.assertTrue(mock_run_deploy.called)
        mock_docker.assert_called_once_with(
            combine_outputs=True,
            ports_mapping=['1440:8000'],
            privilege=True,
            name_prefix='preview',
            timeout=1800,
            env_variables={'GH_TOKEN': 'a-token-one-might-say', 'CI': 'frigg'},
            image='frigg/frigg-test-base'
        )

    @responses.activate
    def test_fetch_task(self):
        responses.add(
            responses.GET,
            'http://example.com',
            body=json.dumps({'job': {'id': 1}}),
            content_type='application/json'
        )

        task = fetch_task('http://example.com', None)
        self.assertEqual(task['id'], 1)

    @patch('frigg_worker.fetcher.upgrade')
    @responses.activate
    def test_fetcher_should_call_upgrade_if_outdated_message_is_returned(self, mock_upgrade):
        responses.add(
            responses.GET,
            'http://example.com',
            status=400,
            body=json.dumps({'error': {'message': '', 'code': 'OUTDATED'}}),
            content_type='application/json'
        )
        fetcher(FETCH_OPTIONS, MagicMock())
        self.assertTrue(mock_upgrade.called)

    @patch('time.sleep')
    @patch('requests.packages.urllib3.response.HTTPResponse.from_httplib',
           side_effect=TimeoutError())
    def test_fetch_task_should_sleep_when_requests_fails(self, mock_send, mock_sleep):
        fetch_task('http://example.com', None)
        mock_sleep.assert_called_once_with(20)
        self.assertTrue(mock_send.called)

    @patch('sys.exit')
    @patch('pip.main')
    def test_upgrade(self, mock_pip, mock_exit):
        upgrade()
        mock_exit.assert_called_once_with(1)
        self.assertEqual(mock_pip.call_args_list, [
            call(['install', '-U', 'frigg-worker']),
            call(['install', '-U', 'frigg-settings']),
            call(['install', '-U', 'frigg-test-discovery']),
            call(['install', '-U', 'docker-wrapper'])
        ])
