from src.exceptions.base import ApplicationException


class EmailAlreadyExistsException(ApplicationException):
    MESSAGE = "Email already exists"


class UsernameAlreadyExistsException(ApplicationException):
    MESSAGE = "Username already exists"

class EmailNotFoundException(ApplicationException):
    MESSAGE = "Email not found"