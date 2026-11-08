import hashlib
import uuid
from datetime import datetime, timezone, timedelta

import jwt


class JWTService:
    def __init__(self,
                 secret: str,
                 algorithm: str,
                 ttl_minutes: int,
                 ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._ttl_minutes = ttl_minutes

    @staticmethod
    def hash_token_raw(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def create_access_token(self, user_id: uuid.UUID) -> str:
        payload = {
            "sub": str(user_id),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self._ttl_minutes),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)
