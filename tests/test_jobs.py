# -*- coding: utf8 -*-
import unittest

from frigg.helpers import ProcessResult
from frigg.jobs import Build, Result

DATA = {
    'id': 2,
    'branch': 'master',
    'sha': 'superbhash',
    'clone_url': 'https://github.com/frigg/test-repo.git',
    'owner': 'frigg',
    'name': 'test-repo',
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
