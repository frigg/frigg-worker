# -*- coding: utf8 -*-
import logging
from os.path import join

import yaml
from frigg.helpers import detect_test_runners

logger = logging.getLogger(__name__)


def build_tasks(directory, docker):
    return detect_test_runners(docker.list_files(directory))


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
