xfrom sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserCodeVerifications


class UserVerificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user_code(self, user_id: int) -> str | None:
        query = select(UserCodeVerifications).where(UserCodeVerifications.user_id == user_id)
        result = await self._session.execute(query)
        verification = result.scalar_one_or_none()
        if verification is None:
            return None
        return verification.code
