# -*- encoding: utf8 -*-
from setuptools import setup, find_packages

setup(
    name='frigg-worker',
    version='0.2.1',
    description='',
    author='The frigg team',
    author_email='hi@frigg.io',
    license='MIT',
    url='https://github.com/frigg/frigg-worker',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'fabric',
        'redis',
        'pyyaml',
        'requests',
        'raven'
    ],
    entry_points={
        'console_scripts': ['frigg-worker = frigg.worker.cli:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
    ]
)
