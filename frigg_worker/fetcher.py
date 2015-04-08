# -*- coding: utf8 -*-
import logging
import random
import time

import requests
from docker.manager import Docker
from frigg.config import config

from .jobs import Build

logger = logging.getLogger(__name__)


def fetcher(**options):
    options = evaluate_options(options)
    while True:
        task = fetch_task(options['dispatcher_url'], options['dispatcher_token'])
        if task:
            start_build(task, options)

        time.sleep(5.0 + random.randint(1, 100) / 100)


def start_build(task, options):

    with Docker() as docker:
        build = Build(task['id'], task, docker=docker, worker_options=options)
        logger.info('Starting %s' % task)
        build.run_tests()


def fetch_task(dispatcher_url, dispatcher_token):
    logger.debug('Fetching new job from {}'.format(dispatcher_url))
    response = requests.get(
        dispatcher_url,
        headers={
            'x-frigg-worker-token': dispatcher_token
        }
    )
    return response.json()['job']


def evaluate_options(options):
    if options['dispatcher_url'] is None:
        options['dispatcher_url'] = config('DISPATCHER_URL')
    if options['dispatcher_token'] is None:
        options['dispatcher_token'] = config('DISPATCHER_TOKEN')
    if options['hq_token'] is None:
        options['hq_token'] = config('HQ_URL')
    if options['hq_url'] is None:
        options['hq_url'] = config('HQ_TOKEN')
    return options
