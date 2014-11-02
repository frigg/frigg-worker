# -*- coding: utf8 -*-
import json
from unittest import TestCase

import mock

from .fetcher import start_task


class TestFetcherCase(TestCase):
    TASK = ('{"branch": "master", "sha": "superbhash", "clone_url": "https://github.com/frigg/frigg-worker.git",'
            '"owner": "frigg", "id": 2, "name": "frigg-worker"}')

    @mock.patch('frigg.worker.fetcher.start_build')
    def test_start_task(self, mock_start_build):
        start_task(self.TASK)
        mock_start_build.assert_called_with(json.loads(self.TASK))

