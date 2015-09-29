# -*- coding: utf8 -*-
import json
import logging
import random
import socket
import sys
import time

import docker
import frigg_coverage
import frigg_settings
import frigg_test_discovery
import pip
import requests
from docker.manager import Docker

import frigg_worker

from .builds import Build
from .deployments import Deployment
from .errors import ApiError

logger = logging.getLogger(__name__)


def fetcher(options, callback):
    notify_of_upstart(options)
    while options['dispatcher_url']:
        try:
            task = fetch_task(options['dispatcher_url'], options['dispatcher_token'])
            if task:
                callback(task, options)
        except ApiError as error:
            if error.code == 'OUTDATED':
                return upgrade()

        time.sleep(5.0 + random.randint(1, 100) / 100)


def fetch_builds(**options):
    return fetcher(options, start_build)


def fetch_deployments(**options):
    return fetcher(options, start_deployment)


def start_build(task, options):
    docker_options = {
        'image': options['docker_image'],
        'combine_outputs': True,
        'privilege': True,
        'env_variables': {'CI': 'frigg', 'GH_TOKEN': task['gh_token']},
        'name_prefix': 'build'
    }
    with Docker(**docker_options) as docker:
        try:
            build = Build(task['id'], task, docker=docker, worker_options=options)
            logger.info('Starting {0}'.format(task))
            build.run_tests()
        except Exception as e:
            logger.exception(e)


def start_deployment(task, options):
    docker_options = {
        'image': task['image'],
        'timeout': task['ttl'],
        'combine_outputs': True,
        'privilege': True,
        'ports_mapping': ['{port}:8000'.format(**task)],
        'env_variables': {'CI': 'frigg', 'GH_TOKEN': task['gh_token']},
        'name_prefix': 'preview'
    }
    docker = Docker(**docker_options)
    docker.start()
    try:
        deployment = Deployment(task['id'], task, docker=docker, worker_options=options)
        deployment.run_deploy()
    except Exception as e:
        docker.stop()
        raise e


def fetch_task(dispatcher_url, dispatcher_token):
    logger.debug('Fetching new job from {0}'.format(dispatcher_url))
    try:
        response = requests.get(
            dispatcher_url,
            headers={
                'x-frigg-worker-token': dispatcher_token,
                'x-frigg-worker-host': socket.gethostname(),
                'x-frigg-worker-version': getattr(frigg_worker, '__version__', ''),
                'x-frigg-settings-version': getattr(frigg_settings, '__version__', ''),
                'x-frigg-coverage-version': getattr(frigg_coverage, '__version__', ''),
                'x-frigg-test-discovery-version': getattr(frigg_test_discovery, '__version__', ''),
                'x-docker-wrapper-version': getattr(docker, '__version__', ''),
            }
        )

        if response.status_code == 200:
            return response.json()['job']
        else:
            raise ApiError(response.json()['error'])
    except requests.exceptions.ConnectionError as e:
        logger.exception(e)

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


def upgrade():
    logger.info('Upgrading worker')
    pip.main(['install', '-U', 'frigg-worker'])
    pip.main(['install', '-U', 'frigg-settings'])
    pip.main(['install', '-U', 'frigg-test-discovery'])
    pip.main(['install', '-U', 'docker-wrapper'])
    sys.exit(1)
