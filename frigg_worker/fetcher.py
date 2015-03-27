# -*- coding: utf8 -*-
import logging
import random
import time

import requests
from frigg.config import config

from .jobs import Build

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
    url = config('DISPATCHER_FETCH_URL')
    logger.debug('Fetching new job from {}'.format(url))
    response = requests.get(
        url,
        headers={
            'x-frigg-worker-token': config('DISPATCHER_TOKEN')
        }
    )
    return response.json()['job']
