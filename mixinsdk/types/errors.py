class RequestError(BaseException):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class RequestTimeout(RequestError):
    def __init__(self, status_code, message):
        if not status_code:
            status_code = 408
        super().__init__(status_code, message)
