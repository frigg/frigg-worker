# -*- coding: utf8 -*-
import logging.config
import os

import click
from frigg.config import config, sentry
from frigg.helpers import local_run

from .fetcher import fetcher

logger = logging.getLogger(__name__)


def load_logging_config():
    try:
        logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'))
    except Exception as e:
        print("There is a problem with the logging config:\n%s" % e)


@click.command()
@click.option('--dispatcher-url', default=None,
              help='The url to the dispatcher, overrides the settings')
def start(dispatcher_url):
    load_logging_config()

    try:
        print("Starting frigg worker")
        local_run("mkdir -p %s" % config('TMP_DIR'))
        fetcher(dispatcher_url)
    except Exception as e:
        logger.error(e)
        sentry.captureException()


if __name__ == '__main__':
    start()
