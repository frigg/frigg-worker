# -*- coding: utf8 -*-
import unittest

import mock
from docker.manager import Docker

from frigg_worker.deployments import Deployment

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
    'deploy_tasks': ['pip install -r requirements.txt', 'gunicorn'],
    'coverage': {'path': 'coverage.xml', 'parser': 'python'}
}

WORKER_OPTIONS = {
    'dispatcher_url': 'http://example.com/dispatch',
    'dispatcher_token': 'tokened',
    'hq_url': 'http://example.com/hq',
    'hq_token': 'tokened',
}


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.docker = Docker()
        self.deployment = Deployment(1, DATA, self.docker, WORKER_OPTIONS)

    @mock.patch('docker.manager.Docker.start')
    @mock.patch('docker.manager.Docker.stop')
    @mock.patch('frigg_worker.deployments.Deployment.clone_repo')
    @mock.patch('frigg_worker.deployments.Deployment.run_task')
    @mock.patch('frigg_worker.deployments.Deployment.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_WITH_NO_SERVICES)
    def test_run_deploy(self, mock_run_task, mock_clone_repo, mock_docker_stop, mock_docker_start):
        self.deployment.run_deploy()
        mock_run_task.assert_has_calls([
            mock.call('pip install -r requirements.txt'),
            mock.call('gunicorn')
        ])
        mock_clone_repo.assert_called_once()
        self.assertTrue(self.deployment.succeeded)
        self.assertTrue(self.deployment.finished)

    @mock.patch('frigg_worker.deployments.Deployment.clone_repo')
    @mock.patch('frigg_worker.deployments.Deployment.run_task', side_effect=OSError())
    @mock.patch('frigg_worker.deployments.Deployment.report_run', lambda *x: None)
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: BUILD_SETTINGS_WITH_NO_SERVICES)
    def test_run_deploy_fail_task(self, mock_run_task, mock_clone_repo):
        self.deployment.run_deploy()
        mock_clone_repo.assert_called_once()
        mock_run_task.assert_has_calls([
            mock.call('pip install -r requirements.txt'),
        ])
        self.assertFalse(self.deployment.succeeded)
        self.assertTrue(self.deployment.finished)

    @mock.patch('frigg_worker.deployments.Deployment.run_task')
    @mock.patch('frigg_worker.deployments.Deployment.clone_repo', lambda x: False)
    def test_run_deploy_fail_clone(self, mock_run_task):
        self.deployment.run_deploy()
        self.assertFalse(mock_run_task.called)
        self.assertFalse(self.deployment.succeeded)

    @mock.patch('frigg_worker.api.APIWrapper.report_run')
    @mock.patch('frigg_worker.deployments.Deployment.serializer', lambda *x: {})
    @mock.patch('frigg_worker.jobs.build_settings', lambda *x: {})
    def test_report_run(self, mock_report_run):
        self.deployment.report_run()
        mock_report_run.assert_called_once_with('Deployment', 1, '{}')
