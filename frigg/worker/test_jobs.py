# -*- coding: utf8 -*-
import json
import unittest
from _pytest.runner import skip
from fabric.operations import _AttributeString

from .jobs import Build, Result

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
        for i in xrange(len(self.build.results)):
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

    @skip('need to check each property')
    def test_serializer(self):
        self.assertEqual(
            json.dumps(self.build, default=Build.serializer),
            '{"sha": "superbhash", "clone_url": "https://github.com/frigg/test-repo.git", "name": "test-repo", '
            '"branch": "master", "owner": "frigg", "id": 1, "results": []}'
        )
        self.assertEqual(json.dumps({'a': 'dict you say'}, default=Build.serializer), '{"a": "dict you say"}' )


class ResultTestCase(unittest.TestCase):

    def test_init_success(self):
        fabric_result = _AttributeString('Success')
        fabric_result.succeeded = True
        fabric_result.return_code = 0
        success = Result('tox', result=fabric_result)
        self.assertTrue(success.succeeded)
        self.assertEquals(success.log, 'Success')
        self.assertEquals(success.task, 'tox')

    def test_init_failure(self):
        fabric_result = _AttributeString('Oh snap')
        fabric_result.succeeded = False
        fabric_result.return_code = 1
        failure = Result('tox', fabric_result)
        self.assertFalse(failure.succeeded)
        self.assertEquals(failure.log, 'Oh snap')
        self.assertEquals(failure.task, 'tox')

    def test_init_error(self):
        error = Result('tox', error='Command not found')
        self.assertFalse(error.succeeded)
        self.assertEquals(error.log, 'Command not found')
        self.assertEquals(error.task, 'tox')
