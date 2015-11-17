frigg-worker |Build status| |Coverage status|
=============================================

A worker application that listens to the frigg broker an pick up builds
and build them.

Setup
-----

::

    virtualenv ~/frigg-worker
    ~/frigg-worker/bin/pip install frigg-worker
    ~/frigg-worker/bin/frigg-worker

Usage
-----

::

    $ frigg_worker --help
    Usage: frigg_worker MODE [OPTIONS]


    Options:
      --dispatcher-url TEXT    URL to the dispatcher, overrides settings
      --dispatcher-token TEXT  Token for dispatcher, overrides settings
      --hq-url TEXT            URL for frigg-hq, overrides settings
      --hq-token TEXT          Token for frigg-hq, overrides settings
      --slack-url TEXT         URL for incoming webhook in slack
      --sentry-dsn TEXT        Sentry dsn needed to connect to the sentry API
      --loglevel TEXT          Set log level for frigg-packages
      --help                   Show this message and exit.


The worker has two modes `builder` and `deployer` which defines whether the worker should
build and run tests or deploy previews.

Builder
~~~~~~~
Runs tasks within a given docker container before removing the docker container and reports
to the build report API of HQ.

Deployer
~~~~~~~~
Starts a docker container that will run for the amount of time specified by the task payload
before running deploy tasks inside the container. The container exposes port 8000 to a port
on the host system given by the task payload. The container-image is chosen from the task
payload, thus, the worker trusts the task-queue to only contain tasks with allowed images.
The status of the deployments is reported to the preview-deployment API of HQ.


Running frigg-worker from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    python -m frigg_worker.cli


--------------

MIT © frigg.io

.. |Build status| image:: https://ci.frigg.io/badges/frigg/frigg-worker/
   :target: https://ci.frigg.io/frigg/frigg-worker/
.. |Coverage status| image:: https://ci.frigg.io/badges/coverage/frigg/frigg-worker/
   :target: https://ci.frigg.io/frigg/frigg-worker/
