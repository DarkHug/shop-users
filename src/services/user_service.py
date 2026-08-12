import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.users import UserCreateDTO, UserCreateDBDTO
from src.exceptions.users import EmailNotFoundException
from src.models import User
from src.repos.user_repo import UserRepository
from src.services.password import PasswordHash


class UserService:
    def __init__(self,
                 password_hash: PasswordHash,
                 user_repository: UserRepository,
                 session: AsyncSession,
                 ):
        self.user_repository = user_repository
        self._session = session
        self.password_hash = password_hash

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