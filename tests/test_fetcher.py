# -*- coding: utf-8 -*-
import json
from unittest import TestCase
from unittest.mock import patch

import responses

from frigg_worker.fetcher import fetch_task, start_build, start_deployment


class FetcherTests(TestCase):
    @patch('frigg_worker.fetcher.Docker')
    @patch('frigg_worker.builds.Build.run_tests')
    def test_start_build(self, mock_run_tests, mock_docker):
        start_build({
            'id': 1,
            'gh_token': 'a-token-one-might-say',
        }, {
            'docker_image': 'frigg/frigg-test-base:latest',
            'hq_token': 'test_token',
            'hq_url': 'url'
        })

        self.assertTrue(mock_run_tests.called)
        mock_docker.assert_called_once_with(
            privilege=True,
            combine_outputs=True,
            image='frigg/frigg-test-base:latest',
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

    @patch('time.sleep')
    @patch('requests.packages.urllib3.response.HTTPResponse.from_httplib',
           side_effect=TimeoutError())
    def test_fetch_task_should(self, mock_send, mock_sleep):
        fetch_task('http://example.com', None)
        mock_sleep.assert_called_once_with(20)
        self.assertTrue(mock_send.called)
