from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from src.uow import UnitOfWork


class UoWProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_uow(self, session: AsyncSession) -> AsyncIterable[UnitOfWork]:
        uow = UnitOfWork(session)
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise
