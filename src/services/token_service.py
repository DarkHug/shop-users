import secrets
import uuid

from src.dtos.auth import TokenReturnDTO, RefreshTokenCreateDBDTO
from src.repos.refresh_token_repo import RefreshTokenRepository
from src.services.jwt_service import JWTService


class TokenService:
    def __init__(self,
                 jwt_service: JWTService,
                 refresh_token_repo: RefreshTokenRepository
                 ):
        self._jwt_service = jwt_service
        self._refresh_token_repo = refresh_token_repo

    async def create_token_pair(self, user_id: uuid.UUID) -> TokenReturnDTO:
        access_token = self._jwt_service.create_access_token(user_id)

        raw_refresh_token = secrets.token_urlsafe(64)

        db_dto = RefreshTokenCreateDBDTO(
            user_id=user_id,
            token_hash=self._jwt_service.hash_token_raw(raw_refresh_token),
            expires_at=self._jwt_service.get_refresh_expiry(),
        )

        await self._refresh_token_repo.create(db_dto)

        return TokenReturnDTO(access_token=access_token, refresh_token=raw_refresh_token)
