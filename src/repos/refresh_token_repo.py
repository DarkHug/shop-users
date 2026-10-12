import uuid

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.auth import RefreshTokenCreateDBDTO
from src.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dto: RefreshTokenCreateDBDTO) -> RefreshToken:
        new_token = insert(RefreshToken).values(dto.model_dump()).returning(RefreshToken)
        result = await self._session.execute(new_token)
        return result.scalar_one()

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        query = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        query = update(RefreshToken).where(RefreshToken.id == token.id).values(revoked=True)
        await self._session.execute(query)

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        query = update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
        await self._session.execute(query)
