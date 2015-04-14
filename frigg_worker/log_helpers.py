# -*- coding: utf-8 -*-
import logging

from frigg.config import config

logger = logging.getLogger(__name__)


def load_logging_config():
    sentry = {}
    handlers = ['console']
    sentry_handler = []
    if config('SENTRY_DSN'):
        handlers = ['console', 'sentry']
        sentry_handler = ['sentry']
        sentry = {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': config('SENTRY_DSN')
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
