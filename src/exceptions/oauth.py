from src.exceptions.base import ExternalServerException


class OAuthCodeExchangeError(ExternalServerException):
    MESSAGE = "OAuth Code Exchange Error"


class OAuthProviderUnavailable(ExternalServerException):
    pass


class OAuthValidationError(ExternalServerException):
    MESSAGE = "OAuth Validation Error"


class OAuthStateInvalid(ExternalServerException):
    MESSAGE = "OAuth State Invalid"


class OAuthEmailNotVerified(ExternalServerException):
    MESSAGE = "OAuth Email not verified"
