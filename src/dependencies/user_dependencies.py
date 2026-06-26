from fastapi import Depends

from src.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.repos.user_repo import UserRepository
from src.repos.user_verification_repo import UserVerificationRepository
from src.services.user_service import UserService
from src.services.verification import VerificationService


async def get_user_service(
        session: AsyncSession = Depends(get_db)
) -> UserService:
    repository = UserRepository(session)
    verification_repository = UserVerificationRepository(session)
    return UserService(repository, session, VerificationService(verification_repository, session))
