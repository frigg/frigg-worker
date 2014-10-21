# -*- coding: utf8 -*-
import json
import time

from frigg.worker import config
from frigg.worker.jobs import Build

builds = []


def fetcher():
    redis = config.redis_client()
    while redis:
        task = redis.rpop('frigg:queue')
        if task:
            __start_task(task)

        time.sleep(2)


def __start_task(json_string):
    task = json.load(json_string)
    build = Build(task.id, task)
    builds.append(build.start_build())
