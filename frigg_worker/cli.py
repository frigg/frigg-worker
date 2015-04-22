# -*- coding: utf8 -*-
import logging.config

import click
from frigg.config import config, sentry

from .fetcher import fetcher
from .log_helpers import load_logging_config

logger = logging.getLogger('frigg_worker.cli')


@click.command()
@click.option('--dispatcher-url', default=None, help='URL to the dispatcher, overrides settings')
@click.option('--dispatcher-token', default=None, help='Token for dispatcher, overrides settings')
@click.option('--hq-url', default=None, help='URl for frigg-hq, overrides settings')
@click.option('--hq-token', default=None, help='Token for frigg-hq, overrides settings')
@click.option('--slack-url', default=None, help='URL for incoming webhook in slack')
@click.option('--loglevel', default='DEBUG', help='Set log level for frigg-packages')
@click.option('--docker-image', default='frigg/frigg-test-base:latest', help='Set docker image')
def start(**options):
    options = evaluate_options(options)
    logging.config.dictConfig(load_logging_config(options))

    try:
        logger.info('Starting frigg worker')
        fetcher(**options)
    except Exception as e:
        logger.error(e)
        sentry.captureException()


def evaluate_options(options):
    if options['dispatcher_url'] is None:
        options['dispatcher_url'] = config('DISPATCHER_URL')
    if options['dispatcher_token'] is None:
        options['dispatcher_token'] = config('DISPATCHER_TOKEN')
    if options['hq_token'] is None:
        options['hq_token'] = config('HQ_TOKEN')
    if options['hq_url'] is None:
        options['hq_url'] = config('HQ_URL')
    if 'slack_icon' not in options:
        options['slack_icon'] = ':monkey_face:'
    if 'slack_channel' not in options:
        options['slack_channel'] = '#workforce'
    if 'docker_image' not in options:
        options['docker_image'] = 'frigg/frigg-test-base:latest'

    options['sentry_dsn'] = config('SENTRY_DSN')
    return options


if __name__ == '__main__':
    start()
