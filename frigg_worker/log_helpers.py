# -*- coding: utf-8 -*-
import logging
import os

logger = logging.getLogger(__name__)


def load_logging_config(options):
    handler_config = {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    }
    handlers = ['console']
    sentry_handler = []
    frigg_level = options['loglevel']
    if options['sentry_dsn'] and 'TESTING' not in os.environ:
        handlers = ['console', 'sentry']
        sentry_handler = ['sentry']
        handler_config['sentry'] = {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': options['sentry_dsn']
        }

    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'console': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%H:%M:%S',
            },
        },
        'handlers': handler_config,
        'loggers': {
            '': {
                'handlers': sentry_handler,
                'level': 'ERROR',
                'propagate': True,
            },
            'requests': {
                'handlers': handlers,
                'level': 'ERROR',
                'propagate': True,
            },
            'docker': {
                'handlers': handlers,
                'level': frigg_level,
                'propagate': True,
            },
            'frigg': {
                'handlers': handlers,
                'level': frigg_level,
                'propagate': True,
            },
            'frigg_coverage': {
                'handlers': handlers,
                'level': frigg_level,
                'propagate': True,
            },
            'frigg_worker': {
                'handlers': handlers,
                'level': frigg_level,
                'propagate': True,
            },
        }
    }
