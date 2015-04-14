# -*- coding: utf-8 -*-
import logging

from frigg.config import config

logger = logging.getLogger(__name__)


def load_logging_config():
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
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.handlers.logging.SentryHandler',
                'dsn': config('SENTRY_DSN')
            },
        },

        'loggers': {
            '': {
                'handlers': ['sentry'],
                'level': 'ERROR',
                'propagate': True,
            },
            'requests': {
                'handlers': ['console', 'sentry'],
                'level': 'ERROR',
                'propagate': True,
            },
            'frigg': {
                'handlers': ['console', 'sentry'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'frigg_coverage': {
                'handlers': ['console', 'sentry'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'frigg_worker': {
                'handlers': ['console', 'sentry'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }
