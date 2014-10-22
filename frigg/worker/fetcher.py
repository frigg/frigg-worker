# -*- coding: utf8 -*-
import json
import time
import logging
import sys

from frigg.worker import config
from frigg.worker.jobs import Build

logger = logging.getLogger(__name__)
builds = []


def fetcher():
    redis = config.redis_client()
    while redis:
        task = redis.rpop('frigg:queue')
        if task:
            __start_task(task)

        time.sleep(2)


def __start_task(json_string):
    task = json.loads(json_string)
    build = Build(task['id'], task)
    builds.append(build.start_build())
    logger.info('Started %s' % build)
