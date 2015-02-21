# -*- coding: utf8 -*-
import json
import logging
import os

from frigg_coverage import parse_coverage

from frigg import api
from frigg.config import config, sentry
from frigg.helpers import cached_property, local_run
from frigg.projects import build_settings

logger = logging.getLogger(__name__)


class Result(object):
    log = ''
    return_code = None
    succeeded = None
    task = None

    def __init__(self, task, result=None, error=None):
        self.task = task
        if result:
            self.succeeded = result.succeeded
            self.return_code = result.return_code
            self.log = result.out
        if error:
            self.log = error or result.err

    @classmethod
    def serialize(cls, obj):
        if isinstance(obj, dict):
            return obj
        return obj.__dict__


class Build(object):
    id = ''
    results = []
    cloned = False
    branch = 'master'
    sha = None
    clone_url = None
    name = None
    owner = None
    pull_request_id = None
    coverage = None

    def __init__(self, build_id, obj):
        self.__dict__.update(obj)
        self.id = build_id
        self.results = []

    @property
    def working_directory(self):
        return os.path.join(config('TMP_DIR'), str(self.id))

    @property
    def succeeded(self):
        for result in self.results:
            if result.succeeded is False:
                return False
        return True

    @cached_property
    def settings(self):
        return build_settings(self.working_directory)

    def run_tests(self):
        self.delete_working_dir()
        if not self.clone_repo():
            return self.error('git clone', 'Access denied')

        try:
            for task in self.settings['tasks']:
                self.run_task(task)

            if self.settings['coverage']:
                self.coverage = parse_coverage(
                    os.path.join(self.working_directory, self.settings['coverage']['path']),
                    self.settings['coverage']['parser']
                )

        except Exception as e:
            self.error('', e)
            sentry.captureException()
            logger.error('Build nr. %s failed\n%s' % (self.id, e.message))
        finally:
            self.delete_working_dir()
            self.report_run()
            logger.info("Run of build %s finished." % self.id)

    def clone_repo(self, depth=1):
        command_options = {
            'depth': depth,
            'url': self.clone_url,
            'pwd': self.working_directory,
            'branch': self.branch,
            'pr_id': self.pull_request_id
        }
        if self.pull_request_id is None:
            clone = local_run("git clone --depth=%(depth)s --branch=%(branch)s "
                              "%(url)s %(pwd)s" % command_options)
        else:
            clone = local_run(
                ("git clone --depth=%(depth)s %(url)s %(pwd)s && cd %(pwd)s "
                 "&& git fetch origin pull/%(pr_id)s/head:pull-%(pr_id)s "
                 "&& git checkout pull-%(pr_id)s") % command_options
            )
        if not clone.succeeded:
            message = "Access denied to %s/%s" % (self.owner, self.name)
            logger.error(message)
        return clone.succeeded

    def run_task(self, task_command):
        run_result = local_run(task_command, self.working_directory)
        self.results.append(Result(task_command, run_result))

    def delete_working_dir(self):
        if os.path.exists(self.working_directory):
            local_run("rm -rf %s" % self.working_directory)

    def error(self, task, message):
        self.results.append(Result(task, error=message))
        self.errored = True

    def report_run(self):
        return api.report_run(self.id, json.dumps(self, default=Build.serializer)).status_code

    @classmethod
    def serializer(cls, obj):
        out = obj.__dict__
        if isinstance(obj, Build):
            out['results'] = [Result.serialize(r) for r in obj.results]
            try:
                out['settings'] = obj.settings
            except RuntimeError:
                pass
        return out
