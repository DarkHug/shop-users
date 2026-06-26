from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, user_data: dict) -> User:
        new_user = User(**user_data)
        self.session.add(new_user)
        await self.session.flush()
        return new_user

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
