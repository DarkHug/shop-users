from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import UserCodeVerifications


class UserVerificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_code(self, user_id: int) -> str | None:
        query = select(UserCodeVerifications).where(UserCodeVerifications.user_id == user_id)
        result = await self.session.execute(query)
        verification = result.scalar_one_or_none()
        if verification is None:
            return None
        return verification.code

    async def get_user_code_object(self, user_id: int) -> str | None:
        query = select(UserCodeVerifications).where(UserCodeVerifications.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_code(self, code: str, user_id: int):
        new_code = UserCodeVerifications(code=code, user_id=user_id)
        self.session.add(new_code)
        await self.session.flush()
        return new_code

    async def update_code(self, code: str, user_id: int):
        old_record = await self.get_user_code_object(user_id)
        if old_record is None:
            return False
        old_record.code = code
        await self.session.flush()
        return True