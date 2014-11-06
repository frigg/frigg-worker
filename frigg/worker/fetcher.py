# -*- coding: utf8 -*-
import json
import time
import logging

from frigg.worker import config
from frigg.worker.jobs import Build

logger = logging.getLogger(__name__)


def fetcher():
    redis = config.redis_client()
    while redis:
        task = redis.rpop('frigg:queue')
        if task:
            start_build(task)

        time.sleep(2)


def start_build(json_string):
    task = json.loads(json_string)
    build = Build(task['id'], task)
    logger.info('Starting %s' % task)
    build.run_tests()
