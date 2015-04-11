# -*- coding: utf-8 -*-
import json
from unittest import TestCase

import responses
from mock import patch

from frigg_worker.fetcher import fetch_task, start_build


def mock_config(key):
    if key == 'DISPATCHER_URL':
        return 'http://example.com'
    if key == 'DISPATCHER_TOKEN':
        return 'token'


class FetcherTestCase(TestCase):

    @patch('docker.manager.Docker.start')
    @patch('docker.manager.Docker.stop')
    @patch('frigg_worker.jobs.Build.run_tests')
    def test_start_build(self, mock_runtests, mock_docker_stop, mock_docker_start):
        start_build({
            'id': 1,
        }, {})

        self.assertTrue(mock_runtests.called)
        self.assertTrue(mock_docker_start.called)
        self.assertTrue(mock_docker_stop.called)

    @patch('frigg_worker.fetcher.config', mock_config)
    @responses.activate
    def test_fetch_task(self):

        responses.add(
            responses.GET,
            mock_config('DISPATCHER_URL'),
            body=json.dumps({'job': {'id': 1}}),
            content_type='application/json'
        )

        task = fetch_task('http://example.com', None)
        self.assertEqual(task['id'], 1)

    @patch('frigg_worker.fetcher.config', mock_config)
    @responses.activate
    def test_fetch_task_custom_dispatcher(self):

        responses.add(
            responses.GET,
            'http://dispatcher.io',
            body=json.dumps({'job': {'id': 1}}),
            content_type='application/json'
        )

        task = fetch_task('http://dispatcher.io', dispatcher_token=None)
        self.assertEqual(task['id'], 1)
