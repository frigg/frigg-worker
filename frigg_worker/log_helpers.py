# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


def load_logging_config(options):
    sentry = {}
    handlers = ['console']
    sentry_handler = []
    if options['sentry_dsn']:
        handlers = ['console', 'sentry']
        sentry_handler = ['sentry']
        sentry = {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': options['sentry_dsn']
        }

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console'
            },
            'sentry': sentry,
        },

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
            'frigg': {
                'handlers': handlers,
                'level': 'DEBUG',
                'propagate': True,
            },
            'frigg_coverage': {
                'handlers': handlers,
                'level': 'DEBUG',
                'propagate': True,
            },
            'frigg_worker': {
                'handlers': handlers,
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }
