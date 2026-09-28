import hashlib
import hmac


class PasswordHash:
    def __init__(self, pepper: str, hash_iterations: int) -> None:
        self._pepper = pepper
        self._hash_iterations = hash_iterations

    def hash(self, password: str, salt: str) -> str:
        password_to_hash = password + salt + self._pepper
        for i in range(self._hash_iterations):
            password_to_hash = hashlib.sha256(password_to_hash.encode()).hexdigest()
        return password_to_hash

    def verify(self, plain_password: str, db_password: str, salt: str) -> bool:
        return hmac.compare_digest(self.hash(plain_password, salt), db_password)
