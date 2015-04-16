frigg-worker |Build status| |Coverage status| |reqiuresio|
==========================================================

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
    Usage: frigg_worker [OPTIONS]

    Options:
      --dispatcher-url TEXT    URL to the dispatcher, overrides settings
      --dispatcher-token TEXT  Token for dispatcher, overrides settings
      --hq-url TEXT            URl for frigg-hq, overrides settings
      --hq-token TEXT          Token for frigg-hq, overrides settings
      --slack-url TEXT         URL for incoming webhook in slack
      --loglevel TEXT          Set log level for frigg-packages
      --help                   Show this message and exit.

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
.. |reqiuresio| image:: https://requires.io/github/frigg/frigg-worker/requirements.svg?branch=master
     :target: https://requires.io/github/frigg/frigg-worker/requirements/?branch=master
     :alt: Requirements Status
