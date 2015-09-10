# -*- encoding: utf8 -*-
import re
import sys
import codecs
from os import path
from setuptools import setup, find_packages


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

with open('frigg_worker/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)

setup(
    name='frigg-worker',
    version=version,
    description='A worker application that listens to the frigg broker '
                'an pick up builds and build them.',
    long_description=read('README.rst'),
    author='The frigg team',
    author_email='hi@frigg.io',
    license='MIT',
    url='https://github.com/frigg/frigg-worker',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'click==5.1',
        'frigg-coverage>=1.0.0,<2.0.0',
        'frigg-test-discovery>=1.0.0,<2.0.0',
        'docker-wrapper>=1.0,<1.1',  # rq.filter: <2.0
        'pyyaml==3.11',
        'requests>=2.0.0,<3.0.0',
        'raven==5.5.0'
    ],
    entry_points={
        'console_scripts': ['frigg-worker = frigg_worker.cli:start']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
    ]
)
