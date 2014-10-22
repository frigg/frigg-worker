# -*- coding: utf8 -*-
from fabric import colors
from frigg.worker.fetcher import fetcher


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

    parser = argparse.ArgumentParser(description='Do some work for frigg.')
    parser.add_argument('command')

    args = parser.parse_args()

    getattr(Commands, args.command, Commands.unknown_command)()

if __name__ == '__main__':
    main()