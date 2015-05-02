# -*- coding: utf8 -*-
import logging
from os.path import join

import yaml
from frigg_test_discovery import detect_test_tasks

logger = logging.getLogger(__name__)


def build_tasks(directory, docker):
    return detect_test_tasks(docker.list_files(directory))


def load_settings_file(path, docker):
    return yaml.load(docker.read_file(path))


def get_path_of_settings_file(directory, docker):
    if docker.file_exist(join(directory, '.frigg.yml')):
        return join(directory, '.frigg.yml')
    elif docker.file_exist(join(directory, '.frigg.yaml')):
        return join(directory, '.frigg.yaml')


def build_settings(directory, docker):
    path = get_path_of_settings_file(directory, docker)

    settings = {
        'setup_tasks': [],
        'tasks': [],
        'webhooks': [],
        'services': []
    }

    if path is not None:
        settings.update(load_settings_file(path, docker))
    else:
        settings['tasks'] = build_tasks(directory, docker)

    if len(settings['tasks']) == 0:
        raise RuntimeError('No tasks found')

    return settings


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
