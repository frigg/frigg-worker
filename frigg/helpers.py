# -*- coding: utf8 -*-
import logging
from time import sleep
from os import listdir
from os.path import isfile, join
from datetime import datetime
from fabric.context_managers import settings

from fabric.operations import local

logger = logging.getLogger(__name__)


def local_run(command):
    """
    Makes sure both stderr and stdout is in the fabric.operations.local output
    """
    with settings(warn_only=True):
        return local('%s 2>&1' % command, capture=True)


def detect_test_runners(build):
    try:
        files = _list_files(build.working_directory)
    except OSError, e:
        files = []
        logger.error('Could not read files in build %s: \n %s' % (build.id, e.message))
    return _detect_test_runners(files)


def _detect_test_runners(files):
    if 'Makefile' in files:
        return ['make test']
    if 'tox.ini' in files:
        return ['tox', 'flake8']
    if 'setup.py' in files:
        return ['python setup.py test', 'flake8']
    if 'manage.py' in files:
        return ['python manage.py test', 'flake8']
    if 'package.json' in files:
        return ['npm install', 'npm test']
    if 'build.sbt' in files:
        return ['sbt test']
    if 'Cargo.toml' in files:
        return ['cargo test']
    if '_config.yml' in files:
        return ['jekyll build']
    return []


def test__detect_test_runners():
    assert(_detect_test_runners([]) == [])
    assert(_detect_test_runners(['random file']) == [])
    files = ['_config.yml', 'Cargo.toml', 'build.sbt', 'package.json', 'manage.py', 'setup.py',
             'tox.ini', 'Makefile']
    assert(_detect_test_runners(files) == ['make test'])
    del files[len(files) - 1]
    assert(_detect_test_runners(files) == ['tox', 'flake8'])
    del files[len(files) - 1]
    assert(_detect_test_runners(files) == ['python setup.py test', 'flake8'])
    del files[len(files) - 1]
    assert(_detect_test_runners(files) == ['python manage.py test', 'flake8'])
    del files[len(files) - 1]
    assert(_detect_test_runners(files) == ['npm install', 'npm test'])
    del files[len(files) - 1]
    assert(_detect_test_runners(files) == ['sbt test'])
    del files[len(files) - 1]
    assert(_detect_test_runners(files) == ['cargo test'])
    del files[len(files) - 1]
    assert(_detect_test_runners(files) == ['jekyll build'])


def _list_files(path):
    return [f for f in listdir(path) if isfile(join(path, f))]


class CachedProperty(object):
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


cached_property = CachedProperty


def test_cached_property():
    class A(object):
        @cached_property
        def func(self):
            return datetime.now().microsecond

    a = A()
    first = a.func
    sleep(0.1)
    last = a.func
    assert(first == last)
