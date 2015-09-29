# -*- coding: utf-8 -*-
import logging
import socket

import requests

logger = logging.getLogger(__name__)


class APIWrapper(object):

    def __init__(self, options):
        self.token = options['hq_token']
        self.url = options['hq_url']

    @property
    def headers(self):
        return {
            'content-type': 'application/json',
            'FRIGG_WORKER_TOKEN': self.token,
            'x-frigg-worker-host': socket.getfqdn()
        }

    def get(self, url):
        return requests.post(url, headers=self.headers)

    def post(self, url, data):
        return requests.post(url, data=data, headers=self.headers)

    def report_run(self, endpoint, build_id, build):
        response = self.post(self.url, data=build)
        logger.info('Reported build to hq, hq response status-code: {0}, data:\n{1}'.format(
            response.status_code,
            build
        ))
        if response.status_code != 200:
            logger.error('Report of build failed, response status-code: {0}, data:\n{1}'.format(
                response.status_code,
                build
            ))
            with open('build-{0}-hq-response.html'.format(build_id), 'w') as f:
                f.write(response.text)
        return response
