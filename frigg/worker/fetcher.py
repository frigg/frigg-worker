# -*- coding: utf8 -*-
import json
import threading
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
            __start_task(task)

        time.sleep(2)


def __start_task(json_string):
    task = json.loads(json_string)
    thread = threading.Thread(name='build-%s' % task['id'], target=__start_build, args=[task])
    thread.daemon = True
    thread.start()
    logger.info('Started %s' % task)
    return thread


def __start_build(task):
    build = Build(task['id'], task)
    build.run_tests()
    for result in build.results:
        del result
    del build
