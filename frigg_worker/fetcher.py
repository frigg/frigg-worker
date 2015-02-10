# -*- coding: utf8 -*-
import logging
import random
import time

import requests

from frigg import Build
from frigg.config import config

logger = logging.getLogger(__name__)


def fetcher():
    while True:
        task = fetch_task()
        if task:
            start_build(task)

        time.sleep(5.0 + random.randint(1, 100) / 100)


def start_build(task):
    build = Build(task['id'], task)
    logger.info('Starting %s' % task)
    build.run_tests()


def fetch_task():
    response = requests.get(
        config('DISPATCHER_FETCH_URL'),
        headers={
            'x-frigg-worker-token': config('DISPATCHER_TOKEN')
        }
    )
    return response.json()['job']
