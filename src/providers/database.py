from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.settings import settings
from typing import NewType, AsyncIterable

DatabaseURL = NewType("DatabaseURL", str)


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def get_secret_value(self) -> DatabaseURL:
        return DatabaseURL(settings.db.url.get_secret_value())

    @provide
    def get_engine(self, url: DatabaseURL) -> AsyncEngine:
        return create_async_engine(url, pool_pre_ping=True)

    @provide
    def get_session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
