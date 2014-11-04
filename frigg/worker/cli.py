# -*- coding: utf8 -*-
import getpass
import os
import logging.config

from fabric import colors

from .fetcher import fetcher
from .config import sentry, config
from frigg.helpers import local_run

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
        print(colors.green("Starting frigg worker"))
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
        print(colors.red("Unknown command"))


def main():
    import argparse

    try:
        logging.config.fileConfig(os.path.expanduser('~/.frigg/logging.conf'))
    except Exception, e:
        print("There is a problem with the logging config:\n%s" % e)

    parser = argparse.ArgumentParser(description='Do some work for frigg.')
    parser.add_argument('command')

    args = parser.parse_args()

    try:
        getattr(Commands, args.command.replace('-', '_'), Commands.unknown_command)()
    except Exception, e:
        logger.error(e)
        sentry.captureException()


if __name__ == '__main__':
    main()
