# -*- coding: utf8 -*-
import logging.config
import os

import click
from frigg.config import sentry

from .fetcher import fetcher

logger = logging.getLogger(__name__)


def load_logging_config():
    try:
        logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'))
    except Exception as e:
        print("There is a problem with the logging config:\n%s" % e)


@click.command()
@click.option('--dispatcher-url', default=None, help='URL to the dispatcher, overrides settings')
@click.option('--dispatcher-token', default=None, help='Token for dispatcher, overrides settings')
@click.option('--hq-url', default=None, help='URl for frigg-hq, overrides settings')
@click.option('--hq-token', default=None, help='Token for frigg-hq, overrides settings')
@click.option('--slack-url', default=None, help='URL for incoming webhook in slack')
def start(**kwargs):
    load_logging_config()

    try:
        print("Starting frigg worker")
        fetcher(**kwargs)
    except Exception as e:
        print(e)
        logger.error(e)
        sentry.captureException()


if __name__ == '__main__':
    start()
