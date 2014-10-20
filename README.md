# frigg-worker

A worker application that listens to the frigg broker an pick up builds and build them.

## Setup
```
virtualenv ~/frigg-worker
~/frigg-worker/bin/pip install -e git+https://github.com/frigg/frigg-worker.git#egg=frigg-worker
~/frigg-worker/bin/frigg-worker start
```