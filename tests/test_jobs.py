# -*- coding: utf8 -*-
import unittest

import mock
from docker.helpers import ProcessResult
from docker.manager import Docker
from raven import Client

from frigg_worker.jobs import Job, Result

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
    'worker_host': 'albus.frigg.io'
}


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.docker = Docker()
        self.job = Job(1, DATA, self.docker, WORKER_OPTIONS)

    def test_init(self):
        self.assertEquals(self.job.id, 1)
        self.assertEquals(len(self.job.results), 0)
        self.assertEquals(self.job.branch, DATA['branch'])
        self.assertEquals(self.job.sha, DATA['sha'])
        self.assertEquals(self.job.sha, DATA['sha'])
        self.assertEquals(self.job.clone_url, DATA['clone_url'])
        self.assertEquals(self.job.owner, DATA['owner'])
        self.assertEquals(self.job.name, DATA['name'])
        self.assertEquals(self.job.worker_host, 'albus.frigg.io')

    def test_error(self):
        self.job.error('tox', 'Command not found')
        self.assertEquals(len(self.job.results), 1)
        self.assertTrue(self.job.errored)
        self.assertFalse(self.job.results['tox'].succeeded)
        self.assertEquals(self.job.results['tox'].log, 'Command not found')
        self.assertEquals(self.job.results['tox'].task, 'tox')

    @mock.patch('docker.manager.Docker.start')
    @mock.patch('docker.manager.Docker.stop')
    @mock.patch('docker.manager.Docker.run')
    def test_succeeded(self, mock_docker_run, mock_docker_stop, mock_docker_start):
        success = Result('tox')
        success.succeeded = True
        failure = Result('flake8')
        failure.succeeded = False
        self.job.results['tox'] = success
        self.assertTrue(self.job.succeeded)
        self.job.results['flake8'] = failure
        self.assertFalse(self.job.succeeded)

    @mock.patch('frigg_worker.api.APIWrapper.report_run')
    @mock.patch('frigg_worker.jobs.Job.serializer', lambda *x: {})
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: {})
    def test_report_run(self, mock_report_run):
        self.job.report_run()
        mock_report_run.assert_called_once_with('Job', 1, '{}')

    @mock.patch('docker.manager.Docker.directory_exist')
    @mock.patch('docker.manager.Docker.run')
    def test_delete_working_dir(self, mock_local_run, mock_directory_exist):
        self.job.delete_working_dir()
        mock_directory_exist.assert_called_once()
        mock_local_run.assert_called_once_with('rm -rf ~/builds/1')

    @mock.patch('docker.manager.Docker.run')
    def test_run_task(self, mock_local_run):
        self.job.results['tox'] = Result('tox')
        self.job.run_task('tox')
        mock_local_run.assert_called_once_with('tox', '~/builds/1')
        self.assertEqual(len(self.job.results), 1)
        self.assertEqual(self.job.results['tox'].task, 'tox')
        self.assertEqual(self.job.results['tox'].pending, False)

    @mock.patch('docker.manager.Docker.run')
    def test_clone_repo_regular(self, mock_local_run):
        self.job.clone_repo(1)
        mock_local_run.assert_called_once_with(
            'git clone --depth=1 --branch=master https://github.com/frigg/test-repo.git ~/builds/1'
            ' && cd ~/builds/1 && git reset --hard superbhash'
        )

    @mock.patch('docker.manager.Docker.start')
    @mock.patch('docker.manager.Docker.stop')
    @mock.patch('docker.manager.Docker.run')
    def test_clone_repo_pull_request(self, mock_local_run, mock_docker_stop, mock_docker_start):
        self.job.pull_request_id = 2
        self.job.clone_repo(1)
        mock_local_run.assert_called_once_with(
            'git clone --depth=1 https://github.com/frigg/test-repo.git ~/builds/1 && cd ~/builds/1'
            ' && git fetch origin pull/2/head:pull-2 && git checkout pull-2 && '
            'cd ~/builds/1 && git reset --hard superbhash'
        )

    @mock.patch('docker.manager.Docker.run')
    def test_clone_repo_no_depth(self, mock_local_run):
        self.job.clone_repo(0)
        mock_local_run.assert_called_once_with(
            'git clone  --branch=master https://github.com/frigg/test-repo.git ~/builds/1'
            ' && cd ~/builds/1 && git reset --hard superbhash'
        )

    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_WITH_NO_SERVICES)
    def test_serializer(self):
        self.job.worker_options['sentry'] = Client()
        serialized = Job.serializer(self.job)
        self.assertEqual(serialized['id'], self.job.id)
        self.assertEqual(serialized['finished'], self.job.finished)
        self.assertEqual(serialized['owner'], self.job.owner)
        self.assertEqual(serialized['name'], self.job.name)
        self.assertEqual(serialized['results'], [])
        self.assertNotIn('worker_options', serialized)
        self.assertNotIn('docker', serialized)
        self.assertNotIn('api', serialized)

        self.job.tasks.append('tox')
        self.job.results['tox'] = Result('tox')
        serialized = Job.serializer(self.job)
        self.assertEqual(serialized['setup_results'], [])
        self.assertEqual(serialized['results'], [{'task': 'tox', 'pending': True}])

        result = ProcessResult('tox')
        result.out = 'Success'
        result.return_code = 0
        self.job.results['tox'].update_result(result)
        self.assertEqual(serialized['results'], [{'task': 'tox', 'pending': False, 'log': 'Success',
                                                  'return_code': 0, 'succeeded': True}])

        self.assertEqual(serialized['setup_results'], [])

    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_SERVICES_AND_SETUP)
    def test_serializer_with_setup_and_tasks(self):
        self.job.worker_options['sentry'] = Client()

        self.job.tasks.append('tox')
        self.job.setup_tasks.append('apt-get install nginx')
        self.job.results['tox'] = Result('tox')
        self.job.setup_results['apt-get install nginx'] = Result('apt-get install nginx')
        serialized = Job.serializer(self.job)
        self.assertEqual(serialized['setup_results'], [{'task': 'apt-get install nginx',
                                                        'pending': True}])
        self.assertEqual(serialized['results'], [{'task': 'tox', 'pending': True}])

        result = ProcessResult('tox')
        result.out = 'Success'
        result.return_code = 0
        self.job.results['tox'].update_result(result)

        setup_result = ProcessResult('apt-get install nginx')
        setup_result.out = 'Success'
        setup_result.return_code = 0
        self.job.setup_results['apt-get install nginx'].update_result(setup_result)

        self.assertEqual(serialized['results'], [{'task': 'tox', 'pending': False, 'log': 'Success',
                                                  'return_code': 0, 'succeeded': True}])

        self.assertEqual(serialized['setup_results'], [{'task': 'apt-get install nginx',
                                                        'pending': False, 'log': 'Success',
                                                        'return_code': 0, 'succeeded': True}])
        self.assertIn('worker_host', serialized)

    @mock.patch('docker.manager.Docker.start')
    @mock.patch('docker.manager.Docker.stop')
    @mock.patch('docker.manager.Docker.run')
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_WITH_NO_SERVICES)
    def test_start_no_services(self, mock_docker_run, mock_docker_stop, mock_docker_start):
        self.job.start_services()
        self.assertFalse(mock_docker_run.called)

    @mock.patch('docker.manager.Docker.run')
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_ONE_SERVICE)
    def test_start_one_service(self, mock_docker_run):
        self.job.start_services()
        mock_docker_run.assert_called_once_with('sudo service redis-server start')

    @mock.patch('frigg_worker.jobs.logger.warning')
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_ONE_SERVICE)
    def test_start_unknown_service(self, mock_logger_warning):
        failed_result = ProcessResult('tox')
        failed_result.return_code = 1
        with mock.patch('docker.manager.Docker.run', lambda *x: failed_result):
            self.job.start_services()
            mock_logger_warning.assert_called_with('Service "redis-server" did not start.')

    @mock.patch('docker.manager.Docker.run')
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_FOUR_SERVICES)
    def test_start_four_services_in_order(self, mock_docker_run):
        self.job.start_services()

        mock_docker_run.assert_has_calls([
            mock.call('sudo service redis-server start'),
            mock.call().succeeded.__bool__(),
            mock.call('sudo service postgresql start'),
            mock.call().succeeded.__bool__(),
            mock.call('sudo service nginx start'),
            mock.call().succeeded.__bool__(),
            mock.call('sudo service mongodb start'),
            mock.call().succeeded.__bool__(),
        ])

    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_SERVICES_AND_SETUP)
    def test_create_pending_tasks_splitted_into_setup_tasks_and_tasks(self):
        self.assertEqual([], self.job.tasks)
        self.assertEqual([], self.job.setup_tasks)
        self.job.create_pending_tasks()
        self.assertEqual(["apt-get install nginx"], self.job.setup_tasks)
        self.assertEqual(["tox"], self.job.tasks)


class ResultTestCase(unittest.TestCase):
    def test_update_result_success(self):
        result = ProcessResult('tox')
        result.out = 'Success'
        result.return_code = 0
        success = Result('tox')
        success.update_result(result)
        self.assertTrue(success.succeeded)
        self.assertEquals(success.log, 'Success')
        self.assertEquals(success.task, 'tox')

    def test_update_result_failure(self):
        result = ProcessResult('tox')
        result.out = 'Oh snap'
        result.return_code = 1
        failure = Result('tox')
        failure.update_result(result)
        self.assertFalse(failure.succeeded)
        self.assertEquals(failure.log, 'Oh snap')
        self.assertEquals(failure.task, 'tox')

    def test_update_error(self):
        error = Result('tox')
        error.update_error('Command not found')
        self.assertFalse(error.succeeded)
        self.assertEquals(error.log, 'Command not found')
        self.assertEquals(error.task, 'tox')

    def test_serialize(self):
        error = Result('tox')
        error.update_error('Command not found')
        self.assertEqual(Result.serialize(error), error.__dict__)
        self.assertEqual(Result.serialize(Result.serialize(error)), error.__dict__)
