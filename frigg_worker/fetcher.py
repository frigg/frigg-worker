# -*- coding: utf8 -*-
import logging
import random
import time

import requests
from frigg.config import config

from .jobs import Build

logger = logging.getLogger(__name__)


def fetcher(dispatcher_url=None, dispatcher_token=None):
    while True:
        task = fetch_task(dispatcher_url, dispatcher_token)
        if task:
            start_build(task)

        time.sleep(5.0 + random.randint(1, 100) / 100)


def start_build(task):
    build = Build(task['id'], task)
    logger.info('Starting %s' % task)
    build.run_tests()


def fetch_task(dispatcher_url, dispatcher_token):
    if dispatcher_url is None:
        dispatcher_url = config('DISPATCHER_FETCH_URL')
    if dispatcher_token is None:
        dispatcher_token = config('DISPATCHER_TOKEN')

    logger.debug('Fetching new job from {}'.format(dispatcher_url))
    response = requests.get(
        dispatcher_url,
        headers={
            'x-frigg-worker-token': dispatcher_token
        }
    )
    return response.json()['job']
