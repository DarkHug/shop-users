from dishka import Provider, Scope, provide
from src.services.password import PasswordHash
from typing import NewType

from src.settings import settings

PasswordPepper = NewType("PasswordPepper", str)


class PasswordProvider(Provider):
    scope = Scope.APP

    @provide
    def get_secret_pepper(self) -> PasswordPepper:
        return PasswordPepper(settings.password.pepper.get_secret_value())

    @provide
    def password_hash(self, pepper: PasswordPepper) -> PasswordHash:
        return PasswordHash(pepper=pepper)
