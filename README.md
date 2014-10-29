# frigg-worker
[![Build status](https://ci.frigg.io/badges/frigg/frigg-worker/)](https://ci.frigg.io/frigg/frigg-worker/)

A worker application that listens to the frigg broker an pick up builds and build them.

## Setup
```
virtualenv ~/frigg-worker
~/frigg-worker/bin/pip install -e git+https://github.com/frigg/frigg-worker.git#egg=frigg-worker
~/frigg-worker/bin/frigg-worker start
```

### Supervisor config
```
[program:frigg-worker]
directory=/home/frigg/
command=/home/frigg/frigg-worker/bin/frigg-worker start
autostart=true
autorestart=true
redirect_stderr=true
user=frigg
```
