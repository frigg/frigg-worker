# -*- coding: utf8 -*-
import os
import yaml

import redis
from raven import Client


def config(key):
    settings = yaml.load(open(os.path.join(os.path.dirname(__file__), 'defaults.yml')))
    try:
        settings.update(yaml.load(open(os.path.expanduser('~/.frigg/worker.yaml'))))
    except IOError:
        pass
    return settings.get(key, None)


def test_config():
    assert(config('REDIS')['host'] == 'localhost')
    assert(config('REDIS')['port'] == 6379)
    assert(config('REDIS')['db'] == 2)
    assert(config('REDIS')['password'] is None)


def redis_client():
    return redis.Redis(
        host=config('REDIS')['host'],
        port=config('REDIS')['port'],
        db=config('REDIS')['db'],
        password=config('REDIS')['password']
    )

sentry = Client(config('SENTRY_DSN'))
