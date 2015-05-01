# -*- coding: utf8 -*-
import json
import logging
import os

import requests
from frigg_coverage import parse_coverage

from frigg_worker.build_helpers import build_settings, cached_property

from . import api

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

    def __init__(self, build_id, obj, docker, worker_options=None):
        self.__dict__.update(obj)
        self.id = build_id
        self.results = {}
        self.tasks = []
        self.finished = False
        self.docker = docker
        self.worker_options = worker_options
        if worker_options:
            self.api = api.APIWrapper(worker_options)

    @property
    def working_directory(self):
        return os.path.join('builds', str(self.id))

    @property
    def succeeded(self):
        for key in self.results:
            if self.results[key].succeeded is False:
                return False
        return True

    @cached_property
    def settings(self):
        return build_settings(self.working_directory, self.docker)

    def run_tests(self):
        task = None
        self.delete_working_dir()
        if not self.clone_repo():
            return self.error('git clone', 'Access denied')

        try:
            self.start_services()
            self.finished = False
            self.create_pending_tasks()
            self.report_run()
            for task in self.settings['tasks']:
                self.run_task(task)
                self.report_run()

            self.parse_coverage()

        except Exception as e:
            self.error(task or '', e)
            logger.exception(e)
            logger.info('Build nr. {build.id} failed\n{0}'.format(str(e), build=self))
        finally:
            self.delete_working_dir()
            self.finished = True
            self.report_run()

            logger.info('Run of build {build.id} finished.'.format(build=self))

    def clone_repo(self, depth=1):
        if self.pull_request_id is None:
            command = (
                'git clone --depth={depth} --branch={build.branch} {build.clone_url} '
                '{build.working_directory}'
            )
        else:
            command = (
                'git clone --depth={depth} {build.clone_url} {build.working_directory} && '
                'cd {build.working_directory} && '
                'git fetch origin pull/{build.pull_request_id}/head:pull-{build.pull_request_id} &&'
                ' git checkout pull-{build.pull_request_id}'
            )

        clone = self.docker.run(command.format(build=self, depth=depth))
        if not clone.succeeded:
            message = 'Access denied to {build.owner}/{build.name}'.format(build=self)
            logger.error(message)
        return clone.succeeded

    def start_services(self):
        for service in self.settings['services']:
            if not self.docker.run('sudo service {0} start'.format(service)).succeeded:
                logger.warning('Service "{0}" did not start.'.format(service))

    def run_task(self, task_command):
        run_result = self.docker.run(task_command, self.working_directory)
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

    def parse_coverage(self):
        if 'coverage' in self.settings:
            try:
                coverage_file = os.path.join(
                    self.working_directory,
                    self.settings['coverage']['path']
                )
                self.coverage = parse_coverage(
                    self.docker.read_file(coverage_file),
                    self.settings['coverage']['parser']
                )
            except Exception as e:
                logger.exception(e)

    def delete_working_dir(self):
        if self.docker.directory_exist(self.working_directory):
            self.docker.run('rm -rf {build.working_directory}'.format(build=self))

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
        try:
            return self.api.report_run(self.id, json.dumps(self, default=Build.serializer)) \
                .status_code
        except requests.exceptions.ConnectionError as e:
            logger.exception(e)
            return 500

    @classmethod
    def serializer(cls, obj):
        out = {}
        if isinstance(obj, Build):
            unwanted = ['worker_options', 'api', 'docker']
            for key in obj.__dict__.keys():
                if key not in unwanted:
                    out[key] = obj.__dict__[key]

            out['results'] = [Result.serialize(obj.results[key]) for key in obj.tasks]
            try:
                out['settings'] = obj.settings
            except RuntimeError:
                pass

        return out
