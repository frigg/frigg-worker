# -*- coding: utf-8 -*-
from subprocess import call
import pytest


def has_docker():
    return False
    try:
        return call(['docker', 'ps']) == 0
    except FileNotFoundError:
        return True

needs_docker = pytest.mark.skipif(not has_docker(), reason='requires docker')
