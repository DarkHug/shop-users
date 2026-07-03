from pwdlib import PasswordHash

from src.settings import settings


class PasswordService:
    def __init__(self):
        self.pepper = settings.password.pepper
        self.hasher = PasswordHash.recommended()

    def hash_password(self, password: str) -> str:
        password_with_pepper = password + self.pepper.get_secret_value()
        return self.hasher.hash(password_with_pepper)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        password_with_pepper = password + self.pepper.get_secret_value()
        return self.hasher.verify(password_with_pepper, hashed_password)
