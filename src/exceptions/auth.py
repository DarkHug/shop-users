from src.exceptions.base import ApplicationException


class RefreshTokenExpired(ApplicationException):
    MESSAGE = "Token Expired"


class RefreshTokenNotFound(ApplicationException):
    MESSAGE = "Token Not Found"


class RefreshTokenReused(ApplicationException):
    MESSAGE = "Token Reused"


class AccessTokenExpired(ApplicationException):
    MESSAGE = "Token Expired"


class AccessTokenInvalid(ApplicationException):
    MESSAGE = "Token Invalid"
