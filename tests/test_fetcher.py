# -*- coding: utf-8 -*-
import json
from unittest import TestCase

import responses
from frigg_worker.fetcher import fetch_task, start_build
from mock import patch


def mock_config(key):
    if key == 'DISPATCHER_FETCH_URL':
        return 'http://example.com'
    if key == 'DISPATCHER_TOKEN':
        return 'token'


class FetcherTestCase(TestCase):
    @patch('frigg_worker.jobs.Build.run_tests')
    def test_start_build(self, mock_runtests):
        start_build({
            'id': 1,
        })
        self.assertTrue(mock_runtests.called)

    @patch('frigg_worker.fetcher.config', mock_config)
    @responses.activate
    def test_fetch_task(self):

        responses.add(
            responses.GET,
            mock_config('DISPATCHER_FETCH_URL'),
            body=json.dumps({'job': {'id': 1}}),
            content_type='application/json'
        )

        task = fetch_task()
        self.assertEqual(task['id'], 1)
