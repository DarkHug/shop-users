import uuid

import asyncpg
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.exceptions.users as user_exceptions
from src.dtos.users import UserCreateDBDTO, UserOAuthCreateDBDTO
from src.models import User


class UserRepository:
    _EMAIL_ALREADY_EXISTS_CONSTRAINT_NAME = "ix_users_email"
    _USERNAME_ALREADY_EXISTS_CONSTRAINT_NAME = "ix_users_username"

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dto: UserCreateDBDTO | UserOAuthCreateDBDTO) -> User:
        new_user = insert(User).values(dto.model_dump()).returning(User)

        try:
            result = await self._session.execute(new_user)
        except IntegrityError as e:
            orig = e.orig.__cause__

            if isinstance(orig, asyncpg.UniqueViolationError):
                if orig.constraint_name == self._EMAIL_ALREADY_EXISTS_CONSTRAINT_NAME:
                    raise user_exceptions.EmailAlreadyExistsException
                if orig.constraint_name == self._USERNAME_ALREADY_EXISTS_CONSTRAINT_NAME:
                    raise user_exceptions.UsernameAlreadyExistsException

            raise

        return result.scalar_one()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
