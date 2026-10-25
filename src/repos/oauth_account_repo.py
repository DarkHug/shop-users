from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.users import OAuthAccountCreateDBDTO
from src.models import OAuthAccount
from src.models.oauth import Provider


class OAuthAccountRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_account(self, provider: Provider, sub: str) -> OAuthAccount | None:
        query = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.sub == sub,
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, dto: OAuthAccountCreateDBDTO) -> OAuthAccount:
        new_account = insert(OAuthAccount).values(dto.model_dump()).returning(OAuthAccount)
        result = await self._session.execute(new_account)

        return result.scalar_one()
