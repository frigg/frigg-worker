# -*- coding: utf-8 -*-
import json
from unittest import TestCase
from unittest.mock import patch

import responses

from frigg_worker.fetcher import fetch_task, start_build


class FetcherTests(TestCase):

    @patch('docker.manager.Docker.start')
    @patch('docker.manager.Docker.stop')
    @patch('frigg_worker.builds.Build.run_tests')
    def test_start_build(self, mock_runtests, mock_docker_stop, mock_docker_start):
        start_build({
            'id': 1,
        }, {'docker_image': 'frigg/frigg-test-base:latest',
            'hq_token': 'test_token',
            'hq_url': 'url'})

        self.assertTrue(mock_runtests.called)
        self.assertTrue(mock_docker_start.called)
        self.assertTrue(mock_docker_stop.called)

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
        mock_send.assert_called_once()
