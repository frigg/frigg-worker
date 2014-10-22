# -*- coding: utf8 -*-
import os
import yaml
import logging
import threading

from fabric.context_managers import settings, lcd
from fabric.operations import local

from frigg.helpers import detect_test_runners

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
            self.log = result
        if error:
            self.log = error


class Build(object):
    id = ''
    results = []
    cloned = False
    working_directory = None
    branch = 'master'
    sha = None
    repo_url = None
    name = None
    owner = None
    errored = False

    def __init__(self, id, object):
        self.__dict__.update(object)
        self.id = id

    def start_build(self):
        t = threading.Thread(target=self.run_tests)
        t.setDaemon(True)
        t.start()
        return t

    @property
    def project_directory(self):
        return os.path.dirname(self.working_directory)

    @property
    def succeeded(self):
        if self.errored:
            return False

        for result in self.results:
            if result.succeeded is False:
                return False
        return True

    @property
    def settings(self):
        path = os.path.join(self.working_directory, '.frigg.yml')
        # Default value for project .frigg.yml
        settings = {
            'webhooks': [],
            'comment': False
        }

        try:
            with open(path) as f:
                settings.update(yaml.load(f))
        except IOError:
            settings['tasks'] = detect_test_runners(self)
        return settings

    def run_tests(self):
        self.delete_working_dir()
        if not self.clone_repo():
            return self.error('git clone', 'Access denied')

        try:

            for task in self.settings['tasks']:
                self.run_task(task)
                if self.succeeded is False:
                    # if one task fails, we do not care about the rest
                    break

        except AttributeError, e:
            self.error('', e)

    def clone_repo(self, depth=1):
        local("mkdir -p %s" % self.project_directory)
        with settings(warn_only=True):
            clone = local("git clone --depth=%s --branch=%s %s %s" % (
                depth,
                self.branch,
                self.repo_url,
                self.working_directory
            ), capture=True)
            if not clone.succeeded:
                message = "Access denied to %s/%s" % (self.owner, self.name)
                logger.error(message)
            return clone.succeeded

    def run_task(self, task_command):
        with settings(warn_only=True):
            with lcd(self.working_directory):
                run_result = local(task_command, capture=True)
                self.results.append(Result(task_command, run_result))

    def delete_working_dir(self):
        if os.path.exists(self.working_directory):
            local("rm -rf %s" % self.working_directory)

    def error(self, task, message):
        self.results.append(Result(task, error=message))
        self.errored = True