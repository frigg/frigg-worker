import socket


class FriggWorkerBaseError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = socket.getfqdn()


class ApiError(FriggWorkerBaseError):
    def __init__(self, error):
        self.code = error['code']
        super().__init__(error['message'])


class GitCloneError(FriggWorkerBaseError):
    MESSAGES = {
        'MISSING_BRANCH': 'Branch does not exist',
        'MISSING_COMMIT': 'Commit does not exist',
        'DNS': 'Can not resolve host',
        'EMPTY_REPLY': 'Empty reply from vcs server',
        'UNKNOWN': 'Unknown error cloning',
    }

    def __init__(self, type, stdout, stderr, report_build_as_error, worker_should_quit=False):
        self.type = type
        self.stdout = stdout
        self.stderr = stderr
        self.report_build_as_error = report_build_as_error
        self.worker_should_quit = worker_should_quit
        super().__init__(self.MESSAGES[type])
