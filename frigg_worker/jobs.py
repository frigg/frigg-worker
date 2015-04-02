# -*- coding: utf8 -*-
from copy import deepcopy
import json
import logging
import os

from frigg import api
from frigg.config import config, sentry
from frigg.helpers import cached_property, local_run
from frigg.projects import build_settings
from frigg_coverage import parse_coverage

logger = logging.getLogger(__name__)


class Result(object):
    log = ''
    return_code = None
    succeeded = None
    task = None
    pending = None

    def __init__(self, task):
        self.task = task
        self.pending = True

    def update_result(self, result):
        self.succeeded = result.succeeded
        self.return_code = result.return_code
        self.log = result.out
        self.pending = False

    def update_error(self, error):
        self.log = error
        self.succeeded = False
        self.pending = False

    @classmethod
    def serialize(cls, obj):
        if isinstance(obj, dict):
            return obj
        return obj.__dict__


class Build(object):
    id = ''
    results = None
    cloned = False
    branch = 'master'
    sha = None
    clone_url = None
    name = None
    owner = None
    pull_request_id = None
    coverage = None
    finished = False

    def __init__(self, build_id, obj):
        self.__dict__.update(obj)
        self.id = build_id
        self.results = {}
        self.tasks = []
        self.finished = False

    @property
    def working_directory(self):
        return os.path.join(config('TMP_DIR'), str(self.id))

    @property
    def succeeded(self):
        for key in self.results:
            if self.results[key].succeeded is False:
                return False
        return True

    @cached_property
    def settings(self):
        return build_settings(self.working_directory)

    def run_tests(self):
        task = None
        self.delete_working_dir()
        if not self.clone_repo():
            return self.error('git clone', 'Access denied')

        self.finished = False
        self.create_pending_tasks()

        try:
            for task in self.settings['tasks']:
                self.run_task(task)
                self.report_run()

            if self.settings['coverage']:
                self.coverage = parse_coverage(
                    os.path.join(self.working_directory, self.settings['coverage']['path']),
                    self.settings['coverage']['parser']
                )

        except Exception as e:
            self.error(task or '', e)
            sentry.captureException()
            logger.error('Build nr. %s failed\n%s' % (self.id, str(e)))
        finally:
            self.delete_working_dir()
            self.finished = True
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
        self.results[task_command].update_result(run_result)

    def create_pending_tasks(self):
        """
        Creates pending task results in a dict on self.result with task string as key. It will also
        create a list on self.tasks that is used to make sure the serialization of the results
        creates a correctly ordered list.
        """
        for task in self.settings['tasks']:
            self.tasks.append(task)
            self.results[task] = Result(task)

    def delete_working_dir(self):
        if os.path.exists(self.working_directory):
            local_run("rm -rf %s" % self.working_directory)

    def error(self, task, message):
        self.errored = True
        if task in self.results:
            self.results[task].update_error(message)
        else:
            result = Result(task)
            result.update_error(message)
            self.tasks.append(task)
            self.results[task] = result

    def report_run(self):
        return api.report_run(self.id, json.dumps(self, default=Build.serializer)).status_code

    @classmethod
    def serializer(cls, obj):
        out = deepcopy(obj.__dict__)
        if isinstance(obj, Build):
            out['results'] = [Result.serialize(obj.results[key]) for key in obj.tasks]
            try:
                out['settings'] = obj.settings
            except RuntimeError:
                pass
        return out
