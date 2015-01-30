# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from frigg_worker.fetcher import start_build
from mock import patch


class FetcherTestCase(TestCase):

    @patch('frigg.Build.run_tests')
    def test_start_build(self, mock_runtests):
        start_build(json.dumps({
            'id': 1,
        }))
        self.assertTrue(mock_runtests.called)
