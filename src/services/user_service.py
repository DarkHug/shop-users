import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.auth import TokenReturnDTO, RefreshTokenCreateDBDTO
from src.dtos.users import UserCreateDTO, UserCreateDBDTO
from src.exceptions.auth import RefreshTokenNotFound, RefreshTokenReused, RefreshTokenExpired
from src.exceptions.users import EmailNotFoundException, InvalidCredentialsException, UserNotFoundException
from src.models import User
from src.repos.refresh_token_repo import RefreshTokenRepository
from src.repos.user_repo import UserRepository
from src.services.jwt_service import JWTService
from src.services.password import PasswordHash


class UserService:
    def __init__(self,
                 password_hash: PasswordHash,
                 user_repository: UserRepository,
                 jwt_service: JWTService,
                 refresh_token_repo: RefreshTokenRepository,
                 session: AsyncSession,
                 ):
        self.user_repository = user_repository
        self._session = session
        self.password_hash = password_hash
        self.jwt_service = jwt_service
        self._refresh_token_repo = refresh_token_repo

    async def create(self, dto: UserCreateDTO) -> User:
        salt = secrets.token_hex(64)
        db_dto = UserCreateDBDTO(
            username=dto.username,
            email=dto.email,
            hashed_password=self.password_hash.hash(dto.password, salt),
            password_salt=salt,
        )
        user = await self.user_repository.create(db_dto)
        await self._session.commit()
        return user

    async def get_by_email(self, email: str) -> User:
        result = await self.user_repository.get_by_email(email)
        if result is None:
            raise EmailNotFoundException
        return result

    async def create_token_pair(self, user_id: uuid.UUID) -> TokenReturnDTO:
        access_token = self.jwt_service.create_access_token(user_id)

        raw_refresh_token = secrets.token_urlsafe(64)

        db_dto = RefreshTokenCreateDBDTO(
            user_id=user_id,
            token_hash=self.jwt_service.hash_token_raw(raw_refresh_token),
            expires_at=self.jwt_service.get_refresh_expiry(),
        )

        await self._refresh_token_repo.create(db_dto)
        await self._session.commit()

        return TokenReturnDTO(access_token=access_token, refresh_token=raw_refresh_token)

    async def refresh_tokens(self, raw_refresh_token: str) -> TokenReturnDTO:
        stored_token = await self._refresh_token_repo.get_by_hash(self.jwt_service.hash_token_raw(raw_refresh_token))
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

    async def login(self, email: str, password: str) -> TokenReturnDTO:
        try:
            user = await self.get_by_email(email)
        except EmailNotFoundException:
            raise InvalidCredentialsException

        if not self.password_hash.verify(password, user.hashed_password, user.password_salt):
            raise InvalidCredentialsException

        res = await self.create_token_pair(user_id=user.id)

        return res

    async def logout(self, raw_token: str) -> None:
        stored_token = await self._refresh_token_repo.get_by_hash(self.jwt_service.hash_token_raw(raw_token))
        if stored_token is None:
            raise RefreshTokenNotFound
        await self._refresh_token_repo.revoke(stored_token)
        await self._session.commit()

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        result = await self.user_repository.get_by_id(user_id)
        if result is None:
            raise UserNotFoundException
        return result
