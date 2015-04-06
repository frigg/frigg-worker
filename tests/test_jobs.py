# -*- coding: utf8 -*-
import unittest
from docker.manager import Docker

import mock
from frigg.helpers import ProcessResult

from frigg_worker.jobs import Build, Result

DATA = {
    'id': 1,
    'branch': 'master',
    'sha': 'superbhash',
    'clone_url': 'https://github.com/frigg/test-repo.git',
    'owner': 'frigg',
    'name': 'test-repo',
}

BUILD_SETTINGS = {
    'tasks': ['tox'],
    'coverage': {'path': 'coverage.xml', 'parser': 'python'}
}


class BuildTestCase(unittest.TestCase):
    def setUp(self):
        with Docker() as docker:
            self.build = Build(1, DATA, docker)

    def test_init(self):
        self.assertEquals(self.build.id, 1)
        self.assertEquals(len(self.build.results), 0)
        self.assertEquals(self.build.branch, DATA['branch'])
        self.assertEquals(self.build.sha, DATA['sha'])
        self.assertEquals(self.build.sha, DATA['sha'])
        self.assertEquals(self.build.clone_url, DATA['clone_url'])
        self.assertEquals(self.build.owner, DATA['owner'])
        self.assertEquals(self.build.name, DATA['name'])

    def test_error(self):
        self.build.error('tox', 'Command not found')
        self.assertEquals(len(self.build.results), 1)
        self.assertTrue(self.build.errored)
        self.assertFalse(self.build.results['tox'].succeeded)
        self.assertEquals(self.build.results['tox'].log, 'Command not found')
        self.assertEquals(self.build.results['tox'].task, 'tox')

    def test_succeeded(self):
        success = Result('tox')
        success.succeeded = True
        failure = Result('flake8')
        failure.succeeded = False
        self.build.results['tox'] = success
        self.assertTrue(self.build.succeeded)
        self.build.results['flake8'] = failure
        self.assertFalse(self.build.succeeded)

    @mock.patch('frigg_worker.jobs.parse_coverage')
    @mock.patch('frigg_worker.jobs.Build.clone_repo')
    @mock.patch('frigg_worker.jobs.Build.run_task')
    @mock.patch('docker.manager.Docker.read_file')
    @mock.patch('frigg_worker.jobs.Build.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS)
    def test_run_tests(self, mock_read_file, mock_run_task, mock_clone_repo, mock_parse_coverage):
        self.build.run_tests()
        mock_run_task.assert_called_once_with('tox')
        mock_clone_repo.assert_called_once()
        mock_read_file.assert_called_once_with('builds/1/coverage.xml')
        mock_parse_coverage.assert_called_once()
        self.assertTrue(self.build.succeeded)
        self.assertTrue(self.build.finished)

    @mock.patch('frigg_worker.jobs.Build.clone_repo')
    @mock.patch('frigg_worker.jobs.Build.run_task', side_effect=OSError())
    @mock.patch('frigg_worker.jobs.Build.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: {'tasks': ['tox'], 'coverage': None})
    def test_run_tests_fail_task(self, mock_run_task, mock_clone_repo):
        self.build.run_tests()
        mock_clone_repo.assert_called_once()
        mock_run_task.assert_called_once_with('tox')
        self.assertFalse(self.build.succeeded)
        self.assertTrue(self.build.finished)

    @mock.patch('frigg_worker.jobs.Build.run_task')
    @mock.patch('frigg_worker.jobs.Build.clone_repo', lambda x: False)
    def test_run_tests_fail_clone(self, mock_run_task):
        self.build.run_tests()
        self.assertFalse(mock_run_task.called)
        self.assertFalse(self.build.succeeded)

    @mock.patch('frigg_worker.jobs.api.report_run')
    @mock.patch('frigg_worker.jobs.Build.serializer', lambda *x: {})
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: {})
    def test_report_run(self, mock_report_run):
        self.build.report_run()
        mock_report_run.assert_called_once_with(1, '{}')

    @mock.patch('docker.manager.Docker.directory_exist')
    @mock.patch('docker.manager.Docker.run')
    def test_delete_working_dir(self, mock_local_run, mock_directory_exist):
        self.build.delete_working_dir()
        mock_directory_exist.assert_called_once()
        mock_local_run.assert_called_once_with('rm -rf builds/1')

    @mock.patch('docker.manager.Docker.run')
    def test_run_task(self, mock_local_run):
        self.build.results['tox'] = Result('tox')
        self.build.run_task('tox')
        mock_local_run.assert_called_once_with('tox', 'builds/1')
        self.assertEqual(len(self.build.results), 1)
        self.assertEqual(self.build.results['tox'].task, 'tox')
        self.assertEqual(self.build.results['tox'].pending, False)

    @mock.patch('docker.manager.Docker.run')
    def test_clone_repo_regular(self, mock_local_run):
        self.build.clone_repo(1)
        mock_local_run.assert_called_once_with(
            'git clone --depth=1 --branch=master https://github.com/frigg/test-repo.git builds/1'
        )

    @mock.patch('docker.manager.Docker.run')
    def test_clone_repo_pull_request(self, mock_local_run):
        self.build.pull_request_id = 2
        self.build.clone_repo(1)
        mock_local_run.assert_called_once_with(
            'git clone --depth=1 https://github.com/frigg/test-repo.git builds/1 && cd builds/1 && '
            'git fetch origin pull/2/head:pull-2 && git checkout pull-2'
        )

    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS)
    def test_serializer(self):
        serialized = Build.serializer(self.build)
        self.assertEqual(serialized['id'], self.build.id)
        self.assertEqual(serialized['finished'], self.build.finished)
        self.assertEqual(serialized['owner'], self.build.owner)
        self.assertEqual(serialized['name'], self.build.name)
        self.assertEqual(serialized['results'], [])

        self.build.tasks.append('tox')
        self.build.results['tox'] = Result('tox')
        serialized = Build.serializer(self.build)
        self.assertEqual(serialized['results'], [{'task': 'tox', 'pending': True}])

        result = ProcessResult(out='Success')
        result.succeeded = True
        result.return_code = 0
        self.build.results['tox'].update_result(result)
        self.assertEqual(serialized['results'], [{'task': 'tox', 'pending': False, 'log': 'Success',
                                                  'return_code': 0, 'succeeded': True}])


class ResultTestCase(unittest.TestCase):
    def test_update_result_success(self):
        result = ProcessResult(out='Success')
        result.succeeded = True
        result.return_code = 0
        success = Result('tox')
        success.update_result(result)
        self.assertTrue(success.succeeded)
        self.assertEquals(success.log, 'Success')
        self.assertEquals(success.task, 'tox')

    def test_update_result_failure(self):
        result = ProcessResult(out='Oh snap')
        result.succeeded = False
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
