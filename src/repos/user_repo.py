import asyncpg
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.exceptions.user_exceptions as user_exceptions
from src.dtos.users import UserCreateDBDTO
from src.models import User

UNIQUE_CONSTRAINTS = {
    "ix_users_email": "email",
    "ix_users_username": "username",
}


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dto: UserCreateDBDTO) -> User:
        new_user = insert(User).values(dto.model_dump()).returning(User)
        try:
            result = await self._session.execute(new_user)
        except IntegrityError as e:
            orig = e.orig.__cause__
            if isinstance(orig, asyncpg.UniqueViolationError):
                field = UNIQUE_CONSTRAINTS.get(orig.constraint_name)
            raise user_exceptions.DuplicateFieldError(field)
        return result.scalar_one()

    async def get_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        result = await self._session.execute(query)

        user = result.scalar_one_or_none()
        if user is None:
            raise user_exceptions.EntityNotFoundError(email)

        return user
