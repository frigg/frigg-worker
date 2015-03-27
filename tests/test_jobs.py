# -*- coding: utf8 -*-
import unittest

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
        self.build = Build(1, DATA)

    def tearDown(self):
        for i in range(len(self.build.results)):
            self.build.results.pop()

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
        self.assertFalse(self.build.results[0].succeeded)
        self.assertEquals(self.build.results[0].log, 'Command not found')
        self.assertEquals(self.build.results[0].task, 'tox')

    def test_succeeded(self):
        success = Result('tox')
        success.succeeded = True
        failure = Result('tox')
        failure.succeeded = False
        self.build.results.append(success)
        self.assertTrue(self.build.succeeded)
        self.build.results.append(failure)
        self.assertFalse(self.build.succeeded)

    @mock.patch('frigg_worker.jobs.parse_coverage')
    @mock.patch('frigg_worker.jobs.Build.clone_repo')
    @mock.patch('frigg_worker.jobs.Build.run_task')
    @mock.patch('frigg_worker.jobs.Build.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS)
    def test_run_tests(self, mock_run_task, mock_clone_repo, mock_parse_coverage):
        self.build.run_tests()
        mock_run_task.assert_called_once_with('tox')
        mock_clone_repo.assert_called_once()
        mock_parse_coverage.assert_called_once_with('builds/1/coverage.xml', 'python')
        self.assertTrue(self.build.succeeded)

    @mock.patch('frigg_worker.jobs.Build.clone_repo')
    @mock.patch('frigg_worker.jobs.Build.run_task', side_effect=OSError())
    @mock.patch('frigg_worker.jobs.Build.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: {'tasks': ['tox'], 'coverage': None})
    def test_run_tests_fail_task(self, mock_run_task, mock_clone_repo):
        self.build.run_tests()
        mock_clone_repo.assert_called_once()
        mock_run_task.assert_called_once_with('tox')
        self.assertFalse(self.build.succeeded)

    @mock.patch('frigg_worker.jobs.Build.run_task')
    @mock.patch('frigg_worker.jobs.Build.clone_repo', lambda x: False)
    def test_run_tests_fail_clone(self, mock_run_task):
        self.build.run_tests()
        self.assertFalse(mock_run_task.called)
        self.assertFalse(self.build.succeeded)

    @mock.patch('frigg_worker.jobs.api')
    def test_report_run(self, mock_report_run):
        self.build.report_run()
        mock_report_run.assert_called_once()

    @mock.patch('frigg_worker.jobs.local_run')
    @mock.patch('os.path.exists', lambda x: True)
    def test_delete_working_dir(self, mock_local_run):
        self.build.delete_working_dir()
        mock_local_run.assert_called_once_with('rm -rf builds/1')

    @mock.patch('frigg_worker.jobs.local_run')
    def test_run_task(self, mock_local_run):
        self.build.run_task('tox')
        mock_local_run.assert_called_once_with('tox', 'builds/1')
        self.assertEqual(len(self.build.results), 1)
        self.assertEqual(self.build.results[0].task, 'tox')

    @mock.patch('frigg_worker.jobs.local_run')
    def test_clone_repo_regular(self, mock_local_run):
        self.build.clone_repo(1)
        mock_local_run.assert_called_once_with(
            'git clone --depth=1 --branch=master https://github.com/frigg/test-repo.git builds/1'
        )

    @mock.patch('frigg_worker.jobs.local_run')
    def test_clone_repo_pull_request(self, mock_local_run):
        self.build.pull_request_id = 2
        self.build.clone_repo(1)
        mock_local_run.assert_called_once_with(
            'git clone --depth=1 https://github.com/frigg/test-repo.git builds/1 && cd builds/1 && '
            'git fetch origin pull/2/head:pull-2 && git checkout pull-2'
        )


class ResultTestCase(unittest.TestCase):
    def test_init_success(self):
        result = ProcessResult(out='Success')
        result.succeeded = True
        result.return_code = 0
        success = Result('tox', result=result)
        self.assertTrue(success.succeeded)
        self.assertEquals(success.log, 'Success')
        self.assertEquals(success.task, 'tox')

    def test_init_failure(self):
        result = ProcessResult(out='Oh snap')
        result.succeeded = False
        result.return_code = 1
        failure = Result('tox', result)
        self.assertFalse(failure.succeeded)
        self.assertEquals(failure.log, 'Oh snap')
        self.assertEquals(failure.task, 'tox')

    def test_init_error(self):
        error = Result('tox', error='Command not found')
        self.assertFalse(error.succeeded)
        self.assertEquals(error.log, 'Command not found')
        self.assertEquals(error.task, 'tox')

    def test_serialize(self):
        error = Result('tox', error='Command not found')
        self.assertEqual(Result.serialize(error), error.__dict__)
        self.assertEqual(Result.serialize(Result.serialize(error)), error.__dict__)
