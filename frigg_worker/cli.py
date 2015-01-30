# -*- coding: utf8 -*-
import getpass
import logging.config
import os

from frigg.config import config, sentry
from frigg.helpers import local_run

from .fetcher import fetcher

logger = logging.getLogger(__name__)


SUPERVISOR_TEMPLATE = '''[program:frigg-worker]
directory=%(path)s
command=%(worker_path)s start
autostart=true
autorestart=true
redirect_stderr=true
user=%(user)s'''


class Commands(object):
    @staticmethod
    def start():
        print("Starting frigg worker")
        local_run("mkdir -p %s" % config('TMP_DIR'))
        fetcher()

    @staticmethod
    def supervisor_config():
        print(SUPERVISOR_TEMPLATE % {
            'path': os.getcwd(),
            'worker_path': '%s/frigg-worker/bin/frigg-worker' % os.getcwd(),
            'user': getpass.getuser()
        })

    @staticmethod
    def unknown_command():
        print("Unknown command")


def load_logging_config():
    try:
        logging.config.fileConfig(os.path.join(os.path.dirname(__file__), 'logging.conf'))
    except Exception as e:
        print("There is a problem with the logging config:\n%s" % e)


def main():
    import argparse

    load_logging_config()

    parser = argparse.ArgumentParser(description='Do some work for frigg.')
    parser.add_argument('command')

    args = parser.parse_args()

    try:
        getattr(Commands, args.command.replace('-', '_'), Commands.unknown_command)()
    except Exception as e:
        logger.error(e)
        sentry.captureException()


if __name__ == '__main__':
    main()
