import hashlib
import secrets
import uuid
from datetime import datetime, timezone, timedelta

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.auth import RefreshTokenNotFound, RefreshTokenReused, RefreshTokenExpired
from src.dtos.auth import RefreshTokenCreateDBDTO, TokenReturnDTO
from src.repos.refresh_token_repo import RefreshTokenRepository


class JWTService:
    def __init__(self,
                 secret: str,
                 algorithm: str,
                 ttl_minutes: int,
                 refresh_ttl_day: int,
                 refresh_token_repo: RefreshTokenRepository,
                 session: AsyncSession) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._ttl_minutes = ttl_minutes
        self._refresh_ttl_day = refresh_ttl_day
        self._refresh_token_repo = refresh_token_repo
        self._session = session

    @staticmethod
    def _hash_token_raw(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _create_access_token(self, user_id: uuid.UUID) -> str:
        payload = {
            "sub": str(user_id),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self._ttl_minutes),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    async def create_token_pair(self, user_id: uuid.UUID) -> TokenReturnDTO:
        access_token = self._create_access_token(user_id)

        raw_refresh_token = secrets.token_urlsafe(64)

        db_dto = RefreshTokenCreateDBDTO(
            user_id=user_id,
            token_hash=self._hash_token_raw(raw_refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=self._refresh_ttl_day)
        )

        await self._refresh_token_repo.create(db_dto)
        await self._session.commit()

        return TokenReturnDTO(access_token=access_token, refresh_token=raw_refresh_token)

    async def refresh_tokens(self, raw_refresh_token: str) -> TokenReturnDTO:
        stored_token = await self._refresh_token_repo.get_by_hash(self._hash_token_raw(raw_refresh_token))
        if stored_token is None:
            raise RefreshTokenNotFound
        user_id = stored_token.user_id
        if stored_token.revoked:
            await self._refresh_token_repo.revoke_all_for_user(user_id=user_id)
            raise RefreshTokenReused
        if stored_token.expires_at < datetime.now(timezone.utc):
            raise RefreshTokenExpired

        await self._refresh_token_repo.revoke(stored_token)

        result = await self.create_token_pair(user_id=user_id)
        return result
