# -*- coding: utf8 -*-
import unittest
from unittest import mock

from docker.helpers import ProcessResult
from docker.manager import Docker
from frigg_settings.model import FriggSettings

from frigg_worker.builds import Build
from frigg_worker.errors import GitCloneError

DATA = {
    'id': 1,
    'branch': 'master',
    'sha': 'superbhash',
    'clone_url': 'https://github.com/frigg/test-repo.git',
    'owner': 'frigg',
    'name': 'test-repo',
}

BUILD_SETTINGS_WITH_NO_SERVICES = FriggSettings({
    'setup_tasks': [],
    'tasks': ['tox'],
    'services': [],
    'coverage': {'path': 'coverage.xml', 'parser': 'python'}
})

BUILD_SETTINGS_ONE_SERVICE = FriggSettings({
    'setup_tasks': [],
    'tasks': ['tox'],
    'services': ['redis-server'],
    'coverage': None,
})

BUILD_SETTINGS_FOUR_SERVICES = FriggSettings({
    'setup_tasks': [],
    'tasks': ['tox'],
    'services': ['redis-server', 'postgresql', 'nginx', 'mongodb'],
    'coverage': None,
})

BUILD_SETTINGS_SERVICES_AND_SETUP = FriggSettings({
    'setup_tasks': ['apt-get install nginx'],
    'tasks': ['tox'],
    'services': ['redis-server', 'postgresql', 'nginx', 'mongodb'],
    'coverage': None,
})

BUILD_SETTINGS_WITH_AFTER_TASKS = FriggSettings({
    'tasks': {
        'tests': ['tox'],
        'after_success': ['success_task'],
        'after_failure': ['failure_task'],
    },
})

WORKER_OPTIONS = {
    'dispatcher_url': 'http://example.com/dispatch',
    'dispatcher_token': 'tokened',
    'hq_url': 'http://example.com/hq',
    'hq_token': 'tokened',
}

GIT_ERROR = GitCloneError('UNKNOWN', '', '', True)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.docker = Docker()
        self.build = Build(1, DATA, self.docker, WORKER_OPTIONS)

    @mock.patch('docker.manager.Docker.start')
    @mock.patch('docker.manager.Docker.stop')
    @mock.patch('frigg_worker.builds.parse_coverage')
    @mock.patch('frigg_worker.builds.Build.clone_repo')
    @mock.patch('frigg_worker.builds.Build.run_task')
    @mock.patch('docker.manager.Docker.read_file')
    @mock.patch('frigg_worker.builds.Build.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_WITH_NO_SERVICES)
    def test_run_tests(self, mock_read_file, mock_run_task, mock_clone_repo,
                       mock_parse_coverage, mock_docker_stop, mock_docker_start):
        self.build.run_tests()
        mock_run_task.assert_called_once_with('tox')
        self.assertTrue(mock_clone_repo.called)
        mock_read_file.assert_called_once_with('~/builds/1/coverage.xml')
        self.assertTrue(mock_parse_coverage.called)
        self.assertTrue(self.build.succeeded)
        self.assertTrue(self.build.finished)

    @mock.patch('frigg_worker.builds.Build.clone_repo')
    @mock.patch('frigg_worker.builds.Build.run_task', side_effect=OSError())
    @mock.patch('frigg_worker.builds.Build.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_WITH_NO_SERVICES)
    def test_run_tests_fail_task(self, mock_run_task, mock_clone_repo):
        self.build.run_tests()
        self.assertTrue(mock_clone_repo.called)
        mock_run_task.assert_called_once_with('tox')
        self.assertFalse(self.build.succeeded)
        self.assertTrue(self.build.finished)

    @mock.patch('frigg_worker.builds.Build.run_task')
    @mock.patch('frigg_worker.builds.Build.clone_repo', side_effect=GIT_ERROR)
    def test_run_tests_fail_clone(self, mock_clone, mock_run_task):
        self.build.run_tests()
        self.assertFalse(mock_run_task.called)
        self.assertFalse(self.build.succeeded)

    @mock.patch('frigg_worker.api.APIWrapper.report_run')
    @mock.patch('frigg_worker.builds.Build.serializer', lambda *x: {})
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: {})
    def test_report_run(self, mock_report_run):
        self.build.report_run()
        mock_report_run.assert_called_once_with('Build', 1, '{}')

    @mock.patch('docker.manager.Docker.directory_exist')
    @mock.patch('docker.manager.Docker.run')
    def test_delete_working_dir(self, mock_local_run, mock_directory_exist):
        self.build.delete_working_dir()
        self.assertTrue(mock_directory_exist.called)
        mock_local_run.assert_called_once_with('rm -rf ~/builds/1')

    @mock.patch('docker.manager.Docker.run')
    @mock.patch('frigg_worker.builds.Build.delete_working_dir', lambda x: True)
    @mock.patch('frigg_worker.builds.Build.clone_repo', lambda x: True)
    @mock.patch('frigg_worker.builds.Build.parse_coverage', lambda x: True)
    @mock.patch('frigg_worker.builds.Build.report_run', lambda x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_SERVICES_AND_SETUP)
    def test_build_setup_steps(self, mock_docker_run):
        self.build.run_tests()

        mock_docker_run.assert_has_calls([
            mock.call('sudo service redis-server start'),
            mock.call('sudo service postgresql start'),
            mock.call('sudo service nginx start'),
            mock.call('sudo service mongodb start'),
            mock.call('apt-get install nginx', self.build.working_directory),
            mock.call('tox', self.build.working_directory),
        ])


def test_run_build_should_call_after_success_on_successful_build(mocker):
    mocker.patch('frigg_worker.builds.Build.clone_repo')
    mocker.patch('frigg_worker.builds.Build.run_task')
    mocker.patch('frigg_worker.builds.Build.report_run',)
    mocker.patch('frigg_worker.jobs.build_settings', return_value=BUILD_SETTINGS_WITH_AFTER_TASKS)
    mock_run_after = mocker.patch('frigg_worker.builds.Build.run_after_task')
    build = Build(1, DATA, Docker(), WORKER_OPTIONS)

    build.run_tests()
    mock_run_after.assert_called_once_with('success_task')


def test_run_build_should_call_after_failure_on_failed_build(mocker):
    result = ProcessResult('tox')
    result.return_code = 1
    mocker.patch('frigg_worker.builds.Build.clone_repo')
    mocker.patch('frigg_worker.builds.Build.run_task')
    mocker.patch('frigg_worker.builds.Build.report_run')
    mocker.patch('frigg_worker.builds.Build.succeeded', False)
    mocker.patch('frigg_worker.jobs.build_settings', return_value=BUILD_SETTINGS_WITH_AFTER_TASKS)
    mock_run_after = mocker.patch('frigg_worker.builds.Build.run_after_task')
    build = Build(1, DATA, Docker(), WORKER_OPTIONS)

    build.run_tests()
    mock_run_after.assert_called_once_with('failure_task')
