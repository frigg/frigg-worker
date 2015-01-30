frigg-worker |Build status| |Coverage status|
=============================================

A worker application that listens to the frigg broker an pick up builds
and build them.

Setup
-----

::

    virtualenv ~/frigg-worker
    ~/frigg-worker/bin/pip install frigg-worker
    ~/frigg-worker/bin/frigg-worker start

Supervisor config
~~~~~~~~~~~~~~~~~

::

    [program:frigg-worker]
    directory=/home/frigg/
    command=/home/frigg/frigg-worker/bin/frigg-worker start
    autostart=true
    autorestart=true
    redirect_stderr=true
    user=frigg

--------------

MIT © frigg.io

.. |Build status| image:: https://ci.frigg.io/badges/frigg/frigg-worker/
   :target: https://ci.frigg.io/frigg/frigg-worker/
.. |Coverage status| image:: https://ci.frigg.io/badges/coverage/frigg/frigg-worker/
   :target: https://ci.frigg.io/frigg/frigg-worker/
