class ApplicationException(Exception):
    MESSAGE = "Internal Server Error"

    def __init__(self, message: str | None = None, *args) -> None:
        super().__init__(message, *args)
        if message is None:
            message = self.MESSAGE
        self.message = message


class ExternalServerException(ApplicationException):
    MESSAGE = "External Error"
