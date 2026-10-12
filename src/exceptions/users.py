from src.exceptions.base import ApplicationException


class EmailAlreadyExistsException(ApplicationException):
    MESSAGE = "Email already exists"


class UsernameAlreadyExistsException(ApplicationException):
    MESSAGE = "Username already exists"


class EmailNotFoundException(ApplicationException):
    MESSAGE = "Email not found"


class UserNotFoundException(ApplicationException):
    MESSAGE = "User not found"


class InvalidCredentialsException(ApplicationException):
    MESSAGE = "Invalid credentials"
