# -*- encoding: utf8 -*-
import codecs
from os import path
from setuptools import setup, find_packages


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()

setup(
    name='frigg-worker',
    version='0.8.0',
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
        'click==3.3',
        'frigg-coverage==0.5.0',
        'frigg-common==0.2.0',
        'raven==5.2.0'
    ],
    entry_points={
        'console_scripts': ['frigg-worker = frigg_worker.cli:start']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
    ]
)
