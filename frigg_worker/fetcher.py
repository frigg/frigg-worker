# -*- coding: utf8 -*-
import json
import logging
import time

from frigg import Build, config

logger = logging.getLogger(__name__)


def fetcher():
    redis = config.redis_client()
    while redis:
        task = redis.rpop('frigg:queue')
        if task:
            start_build(task.decode())

        time.sleep(2)


def start_build(json_string):
    task = json.loads(json_string)
    build = Build(task['id'], task)
    logger.info('Starting %s' % task)
    build.run_tests()
