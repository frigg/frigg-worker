# -*- coding: utf8 -*-
import logging
import logging.config

import click
from frigg.config import sentry

from .fetcher import fetcher
from .log_helpers import load_logging_config

logger = logging.getLogger(__name__)


@click.command()
@click.option('--dispatcher-url', default=None, help='URL to the dispatcher, overrides settings')
@click.option('--dispatcher-token', default=None, help='Token for dispatcher, overrides settings')
@click.option('--hq-url', default=None, help='URl for frigg-hq, overrides settings')
@click.option('--hq-token', default=None, help='Token for frigg-hq, overrides settings')
@click.option('--slack-url', default=None, help='URL for incoming webhook in slack')
def start(**kwargs):
    logging.config.dictConfig(load_logging_config())

    try:
        logger.info('Starting frigg worker')
        fetcher(**kwargs)
    except Exception as e:
        logger.error(e)
        sentry.captureException()


if __name__ == '__main__':
    start()
