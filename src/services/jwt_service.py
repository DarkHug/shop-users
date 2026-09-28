import hashlib
import uuid
from datetime import datetime, timezone, timedelta

import jwt

from src.exceptions.auth import AccessTokenExpired, AccessTokenInvalid


class JWTService:
    def __init__(self,
                 secret: str,
                 algorithm: str,
                 ttl_minutes: int,
                 refresh_ttl_day: int,
                 ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._ttl_minutes = ttl_minutes
        self._refresh_ttl_day = refresh_ttl_day

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

    def get_refresh_expiry(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=self._refresh_ttl_day)

    def verify_access_token(self, token: str) -> uuid.UUID:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            raise AccessTokenExpired
        except jwt.InvalidTokenError:
            raise AccessTokenInvalid

        user_id = uuid.UUID(payload.get("sub"))
        return user_id
