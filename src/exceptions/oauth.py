from src.exceptions.base import ExternalServerException


class OAuthCodeExchangeError(ExternalServerException):
    MESSAGE = "OAuth Code Exchange Error"

class OAuthProviderUnavailable(ExternalServerException):
    pass

class OAuthValidationError(ExternalServerException):
    MESSAGE = "OAuth Validation Error"