class FriggWorkerBaseError(Exception):
    pass


class ApiError(FriggWorkerBaseError):
    def __init__(self, error):
        self.code = error['code']
        super().__init__(error['message'])
