# -*- coding: utf8 -*-
import json
import logging
import random
import socket
import time

import requests
from docker.manager import Docker
from frigg.config import config

from .jobs import Build

logger = logging.getLogger(__name__)


def fetcher(**options):
    options = evaluate_options(options)
    notify_of_upstart(options)
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
    if 'slack_icon' not in options:
        options['slack_icon'] = ':monkey_face:'
    if 'slack_channel' not in options:
        options['slack_channel'] = '#workforce'
    return options


def notify_of_upstart(options):
    if options['slack_url']:
        host = socket.gethostname()
        requests.post(options['slack_url'], json.dumps({
            'icon_emoji': options['slack_icon'],
            'channel': options['slack_channel'],
            'text': 'I just started on host {host}, looking for work now...'.format(host=host),
            'username': 'frigg-worker',
        }))
