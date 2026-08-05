import hashlib

from src.settings import settings


class PasswordHash:
    def __init__(self, pepper: str):
        self._pepper = pepper

    def hash(self, password: str, salt: str) -> str:
        password_to_hash = password + salt + self._pepper
        for i in range(settings.password.hash_iterations):
            password_to_hash = hashlib.sha256(password_to_hash.encode()).hexdigest()
        return password_to_hash
