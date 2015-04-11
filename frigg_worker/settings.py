# -*- coding: utf8 -*-
import logging
from os import listdir
from os.path import exists, isfile, join

import yaml

from frigg.helpers import detect_test_runners

logger = logging.getLogger(__name__)


def build_tasks(directory):
    try:
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
    except OSError as e:
        files = []
        logger.error('Could not read files in path {}: \n {}'.format(directory, e))
    return detect_test_runners(files)


def load_settings_file(path):
    with open(path) as f:
        return yaml.load(f)


def get_path_of_settings_file(directory):
    if exists(join(directory, '.frigg.yml')):
        return join(directory, '.frigg.yml')
    elif exists(join(directory, '.frigg.yaml')):
        return join(directory, '.frigg.yaml')


def build_settings(directory):
    path = get_path_of_settings_file(directory)

    settings = {
        'webhooks': [],
        }

    if path is not None:
        settings.update(load_settings_file(path))
    else:
        settings['tasks'] = build_tasks(directory)

    if len(settings['tasks']) == 0:
        raise RuntimeError('No tasks found')

    return settings
