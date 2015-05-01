# -*- coding: utf8 -*-
import json
import logging
import random
import socket
import time

import requests
from docker.manager import Docker

from .jobs import Build

logger = logging.getLogger(__name__)


def fetcher(**options):
    notify_of_upstart(options)
    while options['dispatcher_url']:
        task = fetch_task(options['dispatcher_url'], options['dispatcher_token'])
        if task:
            start_build(task, options)

        time.sleep(5.0 + random.randint(1, 100) / 100)


def start_build(task, options):
    docker_options = {
        'image': options['docker_image'],
        'combine_outputs': True,
        'privilege': True
    }
    with Docker(**docker_options) as docker:
        try:
            build = Build(task['id'], task, docker=docker, worker_options=options)
            logger.info('Starting {0}'.format(task))
            build.run_tests()
        except Exception as e:
            logger.exception(e)


def fetch_task(dispatcher_url, dispatcher_token):
    logger.debug('Fetching new job from {0}'.format(dispatcher_url))
    response = requests.get(
        dispatcher_url,
        headers={
            'x-frigg-worker-token': dispatcher_token
        }
    )

    if response.status_code == 200:
        return response.json()['job']
    else:
        time.sleep(20)


def notify_of_upstart(options):
    if options['slack_url']:
        host = socket.gethostname()
        requests.post(options['slack_url'], json.dumps({
            'icon_emoji': options['slack_icon'],
            'channel': options['slack_channel'],
            'text': 'I just started on host {host}, looking for work now...'.format(host=host),
            'username': 'frigg-worker',
        }))
