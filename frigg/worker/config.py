# -*- coding: utf8 -*-
import os
import yaml

import redis
from raven import Client


def config(key):
    settings = yaml.load(open(os.path.join(os.path.dirname(__file__), 'defaults.yml')))
    paths = [
        '/etc/frigg/worker.yaml',
        os.path.expanduser('~/.frigg/worker.yaml'),
    ]
    for path in paths:
        try:
            settings.update(yaml.load(open(path)))
        except IOError:
            pass
    return settings.get(key, None)


def redis_client():
    return redis.Redis(
        host=config('REDIS')['host'],
        port=config('REDIS')['port'],
        db=config('REDIS')['db'],
        password=config('REDIS')['password']
    )


sentry = Client(config('SENTRY_DSN'))
