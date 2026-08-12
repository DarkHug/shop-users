from typing import AsyncIterable

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

from src.repos.user_repo import UserRepository
from src.services.password import PasswordHash
from src.services.user_service import UserService
from src.settings import Settings


class AppProvider(Provider):
    def __init__(
            self,
            settings: Settings,
    ) -> None:
        super().__init__()
        self._settings = settings

    scope = Scope.APP

    @provide
    def settings(self) -> Settings:
        return self._settings


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def get_engine(self, settings: Settings) -> AsyncEngine:
        return create_async_engine(settings.db.url.get_secret_value(), pool_pre_ping=True)

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


class PasswordProvider(Provider):
    scope = Scope.APP

    @provide
    def password_hash(self, settings: Settings) -> PasswordHash:
        return PasswordHash(settings.password.pepper.get_secret_value(), settings.password.hash_iterations)


class RepoProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_repo(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

class ServiceProvider(Provider):
    scope = Scope.REQUEST
    @provide
    def get_service(self,
                          user_repo: UserRepository,
                          session: AsyncSession,
                          password_hash: PasswordHash,
                          ) -> UserService:
        return UserService(
            password_hash=password_hash,
            user_repository=user_repo,
            session=session,
        )