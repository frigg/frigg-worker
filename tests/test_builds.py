# -*- coding: utf8 -*-
import unittest
from unittest import mock

from docker.manager import Docker

from frigg_worker.builds import Build

DATA = {
    'id': 1,
    'branch': 'master',
    'sha': 'superbhash',
    'clone_url': 'https://github.com/frigg/test-repo.git',
    'owner': 'frigg',
    'name': 'test-repo',
}

BUILD_SETTINGS_WITH_NO_SERVICES = {
    'setup_tasks': [],
    'tasks': ['tox'],
    'services': [],
    'coverage': {'path': 'coverage.xml', 'parser': 'python'}
}

BUILD_SETTINGS_ONE_SERVICE = {
    'setup_tasks': [],
    'tasks': ['tox'],
    'services': ['redis-server'],
    'coverage': None,
}

BUILD_SETTINGS_FOUR_SERVICES = {
    'setup_tasks': [],
    'tasks': ['tox'],
    'services': ['redis-server', 'postgresql', 'nginx', 'mongodb'],
    'coverage': None,
}

BUILD_SETTINGS_SERVICES_AND_SETUP = {
    'setup_tasks': ['apt-get install nginx'],
    'tasks': ['tox'],
    'services': ['redis-server', 'postgresql', 'nginx', 'mongodb'],
    'coverage': None,
}

WORKER_OPTIONS = {
    'dispatcher_url': 'http://example.com/dispatch',
    'dispatcher_token': 'tokened',
    'hq_url': 'http://example.com/hq',
    'hq_token': 'tokened',
}


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
        mock_clone_repo.assert_called_once()
        mock_read_file.assert_called_once_with('~/builds/1/coverage.xml')
        mock_parse_coverage.assert_called_once()
        self.assertTrue(self.build.succeeded)
        self.assertTrue(self.build.finished)

    @mock.patch('frigg_worker.builds.Build.clone_repo')
    @mock.patch('frigg_worker.builds.Build.run_task', side_effect=OSError())
    @mock.patch('frigg_worker.builds.Build.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_WITH_NO_SERVICES)
    def test_run_tests_fail_task(self, mock_run_task, mock_clone_repo):
        self.build.run_tests()
        mock_clone_repo.assert_called_once()
        mock_run_task.assert_called_once_with('tox')
        self.assertFalse(self.build.succeeded)
        self.assertTrue(self.build.finished)

    @mock.patch('frigg_worker.builds.Build.run_task')
    @mock.patch('frigg_worker.builds.Build.clone_repo', lambda x: False)
    def test_run_tests_fail_clone(self, mock_run_task):
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
        mock_directory_exist.assert_called_once()
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
            mock.call().succeeded.__bool__(),
            mock.call('sudo service postgresql start'),
            mock.call().succeeded.__bool__(),
            mock.call('sudo service nginx start'),
            mock.call().succeeded.__bool__(),
            mock.call('sudo service mongodb start'),
            mock.call().succeeded.__bool__(),
            mock.call('apt-get install nginx', self.build.working_directory),
            mock.call('tox', self.build.working_directory),
        ])
