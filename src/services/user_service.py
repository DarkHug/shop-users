from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.users import UserCreateDTO, UserCreateDBDTO
from src.models import User
from src.repos.user_repo import UserRepository
from src.services.password import PasswordService
from src.services.verification import VerificationService


class UserService:
    def __init__(self, user_repository: UserRepository, session: AsyncSession,
                 verifications_service: VerificationService):
        self.user_repository = user_repository
        self._session = session
        self.verifications_service = verifications_service

    async def create(self, dto: UserCreateDTO) -> User:
        db_dto = UserCreateDBDTO(
            username=dto.username,
            email=dto.email,
            hashed_password=PasswordService().hash_password(dto.password),
        )
        user = await self.user_repository.create(db_dto)
        await self._session.commit()
        return user

    async def get_by_email(self, email: str) -> User:
        return await self.user_repository.get_by_email(email)
