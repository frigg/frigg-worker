# -*- coding: utf8 -*-
import logging.config
import socket

import click

from .fetcher import fetch_builds, fetch_deployments
from .log_helpers import load_logging_config

logger = logging.getLogger('frigg_worker.cli')


@click.command()
@click.argument('mode')
@click.option('--dispatcher-url', default=None, help='URL to the dispatcher, overrides settings')
@click.option('--dispatcher-token', default=None, help='Token for dispatcher, overrides settings')
@click.option('--hq-url', default=None, help='URL for frigg-hq, overrides settings')
@click.option('--hq-token', default=None, help='Token for frigg-hq, overrides settings')
@click.option('--slack-url', default=None, help='URL for incoming webhook in slack')
@click.option('--sentry-dsn', default=None, help='Sentry dsn needed to connect to the sentry API')
@click.option('--loglevel', default='DEBUG', help='Set log level for frigg-packages')
@click.option('--docker-image', default='frigg/frigg-test-base:latest',
              help='The docker image, could be either from the registry or a local tag.')
def start(mode, **kwargs):
    options = {
        'slack_icon': ':monkey_face:',
        'slack_channel': '#workforce'
    }
    options.update(kwargs)
    logging.config.dictConfig(load_logging_config(options))

    try:
        from raven import Client
        options['sentry'] = Client(options['sentry_dsn'])
    except ImportError:
        options['sentry'] = None

    options['worker_host'] = socket.getfqdn()

    _start(mode, **options)


def _start(mode, **options):
    try:
        logger.info('Starting frigg worker')
        if mode == 'builder':
            fetch_builds(**options)
        elif mode == 'deployer':
            fetch_deployments(**options)
        else:
            print('Unknown mode {0}'.format(mode))
    except Exception as e:
        logger.exception(e)
        _start(mode, **options)


if __name__ == '__main__':
    start()
