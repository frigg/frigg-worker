# -*- coding: utf8 -*-
import os
import logging.config

from fabric import colors

from .fetcher import fetcher
from .config import sentry


class Commands(object):

    @staticmethod
    def start():
        print(colors.green("Starting frigg worker"))
        fetcher()

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
        getattr(Commands, args.command, Commands.unknown_command)()
    except Exception:
        sentry.captureException()


if __name__ == '__main__':
    main()
