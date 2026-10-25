import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.auth import TokenReturnDTO
from src.dtos.users import UserCreateDTO, UserCreateDBDTO
from src.exceptions.auth import RefreshTokenNotFound, RefreshTokenReused, RefreshTokenExpired
from src.exceptions.users import EmailNotFoundException, InvalidCredentialsException, UserNotFoundException
from src.models import User
from src.repos.refresh_token_repo import RefreshTokenRepository
from src.repos.user_repo import UserRepository
from src.services.jwt_service import JWTService
from src.services.password import PasswordHash
from src.services.token_service import TokenService


class UserService:
    def __init__(self,
                 password_hash: PasswordHash,
                 user_repository: UserRepository,
                 jwt_service: JWTService,
                 refresh_token_repo: RefreshTokenRepository,
                 session: AsyncSession,
                 token_service: TokenService
                 ):
        self._user_repository = user_repository
        self._session = session
        self._password_hash = password_hash
        self._jwt_service = jwt_service
        self._refresh_token_repo = refresh_token_repo
        self._token_service = token_service

    async def create(self, dto: UserCreateDTO) -> User:
        salt = secrets.token_hex(64)
        db_dto = UserCreateDBDTO(
            username=dto.username,
            email=dto.email,
            hashed_password=self._password_hash.hash(dto.password, salt),
            password_salt=salt,
        )
        user = await self._user_repository.create(db_dto)
        await self._session.commit()
        return user

    async def get_by_email(self, email: str) -> User:
        result = await self._user_repository.get_by_email(email)
        if result is None:
            raise EmailNotFoundException
        return result

    async def refresh_tokens(self, raw_refresh_token: str) -> TokenReturnDTO:
        stored_token = await self._refresh_token_repo.get_by_hash(self._jwt_service.hash_token_raw(raw_refresh_token))
        if stored_token is None:
            raise RefreshTokenNotFound
        user_id = stored_token.user_id
        if stored_token.revoked:
            await self._refresh_token_repo.revoke_all_for_user(user_id=user_id)
            await self._session.commit()
            raise RefreshTokenReused
        if stored_token.expires_at < datetime.now(timezone.utc):
            raise RefreshTokenExpired

        await self._refresh_token_repo.revoke(stored_token)

        result = await self._token_service.create_token_pair(user_id=user_id)
        await self._session.commit()
        return result

    async def login(self, email: str, password: str) -> TokenReturnDTO:
        try:
            user = await self.get_by_email(email)
        except EmailNotFoundException:
            raise InvalidCredentialsException

        if user.hashed_password is None or not self._password_hash.verify(password, user.hashed_password, user.password_salt):
            raise InvalidCredentialsException

        res = await self._token_service.create_token_pair(user_id=user.id)
        await self._session.commit()

        return res

    async def logout(self, raw_token: str) -> None:
        stored_token = await self._refresh_token_repo.get_by_hash(self._jwt_service.hash_token_raw(raw_token))
        if stored_token is None:
            raise RefreshTokenNotFound
        await self._refresh_token_repo.revoke(stored_token)
        await self._session.commit()

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        result = await self._user_repository.get_by_id(user_id)
        if result is None:
            raise UserNotFoundException
        return result
