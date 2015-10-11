import os

import pytest as pytest
import requests

from frigg_worker.fetcher import start_build

from . import needs_docker


@pytest.fixture
def latest_commit():
    url = 'https://api.github.com/repos/frigg/frigg-worker/git/refs/heads/master'
    if 'GH_TOKEN' in os.environ:
        url += '?access_token={token}'.format(token=os.environ['GH_TOKEN'])
    response = requests.get(url)
    return response.json()['object']['sha']


@pytest.fixture
def build_options():
    return {
        'hq_token': 'wat',
        'hq_url': 'http://example.com',
    }


@pytest.fixture
def task():
    return {
        'id': 42,
        'image': 'frigg/frigg-test-base',
        'branch': 'master',
        'sha': 'hash',
        'clone_url': 'https://github.com/frigg/frigg-worker.git',
        'gh_token': 'supertoken',
        'owner': 'frigg',
        'name': 'frigg-worker',
    }


@needs_docker
def test_should_build_latest_frigg_worker(mocker, task, latest_commit, build_options):
    mocker.patch('frigg_worker.api.APIWrapper.report_run')
    task.update({'sha': latest_commit})
    build = start_build(task, build_options)
    assert build is not None
    assert len(build.results.keys()) != 0


@needs_docker
def test_should_mark_non_existing_branch_as_error(mocker, task, latest_commit, build_options):
    mocker.patch('frigg_worker.api.APIWrapper.report_run')
    task.update({'branch': 'not-a-branch'})
    build = start_build(task, build_options)
    assert build is not None
    assert build.errored


@needs_docker
def test_should_mark_non_existing_commit_as_error(mocker, task, build_options):
    mocker.patch('frigg_worker.api.APIWrapper.report_run')
    task.update({'sha': '0000000000000000000000000000000000000000'})
    build = start_build(task, build_options)
    assert build is not None
    assert build.errored
