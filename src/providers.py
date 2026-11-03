from typing import AsyncIterable

import httpx
from dishka import Provider, provide, Scope
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

from src.repos.oauth_account_repo import OAuthAccountRepository
from src.repos.oauth_state_repo import OAuthStateRepository
from src.repos.refresh_token_repo import RefreshTokenRepository
from src.repos.user_repo import UserRepository
from src.services.google_auth_service import GoogleAuthService
from src.services.jwt_service import JWTService
from src.services.oauth_github import GitHubOAuthClient
from src.services.oauth_google import GoogleOAuthClient
from src.services.password import PasswordHash
from src.services.token_service import TokenService
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


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_client(self, settings: Settings) -> AsyncIterable[Redis]:
        redis_client = Redis(host=settings.redis.host, port=settings.redis.port)
        yield redis_client

        await redis_client.aclose()


class HTTPXProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_client(self) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient() as client:
            yield client


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

    @provide
    def get_jwt_repo(self, session: AsyncSession) -> RefreshTokenRepository:
        return RefreshTokenRepository(session)

    @provide
    def get_oauth_repo(self, redis: Redis, settings: Settings) -> OAuthStateRepository:
        return OAuthStateRepository(redis, settings.google_oauth.state_ttl_seconds)

    @provide
    def get_oauth_account_repo(self, session: AsyncSession) -> OAuthAccountRepository:
        return OAuthAccountRepository(session)


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_jwt_service(self, settings: Settings) -> JWTService:
        return JWTService(
            secret=settings.jwt.secret_key.get_secret_value(),
            algorithm=settings.jwt.algorithm,
            ttl_minutes=settings.jwt.ttl,
            refresh_ttl_day=settings.jwt.refresh_ttl,
        )

    @provide
    def get_token_service(self,
                          jwt_service: JWTService,
                          refresh_token_repo: RefreshTokenRepository,
                          ) -> TokenService:
        return TokenService(
            jwt_service=jwt_service,
            refresh_token_repo=refresh_token_repo,
        )

    @provide
    def get_user_service(self,
                         user_repo: UserRepository,
                         session: AsyncSession,
                         password_hash: PasswordHash,
                         jwt_service: JWTService,
                         refresh_token_repo: RefreshTokenRepository,
                         token_service: TokenService,
                         ) -> UserService:
        return UserService(
            password_hash=password_hash,
            user_repository=user_repo,
            session=session,
            jwt_service=jwt_service,
            refresh_token_repo=refresh_token_repo,
            token_service=token_service,
        )

    @provide(scope=Scope.APP)
    def get_google_oauth_client(self,
                                settings: Settings,
                                httpx_client: httpx.AsyncClient,
                                ) -> GoogleOAuthClient:
        return GoogleOAuthClient(
            client_id=settings.google_oauth.client_id,
            client_secret=settings.google_oauth.client_secret.get_secret_value(),
            redirect_uri=settings.google_oauth.redirect_uri,
            httpx_client=httpx_client,
        )

    @provide(scope=Scope.APP)
    def get_github_oauth_client(self,
                                settings: Settings,
                                httpx_client: httpx.AsyncClient,
                                ) -> GitHubOAuthClient:
        return GitHubOAuthClient(
            client_id=settings.github_oauth.client_id,
            client_secret=settings.github_oauth.client_secret.get_secret_value(),
            redirect_uri=settings.github_oauth.redirect_uri,
            httpx_client=httpx_client,
        )

    @provide
    def get_google_auth_service(self,
                                session: AsyncSession,
                                oauth_account_repo: OAuthAccountRepository,
                                oauth_state_repo: OAuthStateRepository,
                                user_repo: UserRepository,
                                google_oauth_client: GoogleOAuthClient,
                                token_service: TokenService,
                                ) -> GoogleAuthService:
        return GoogleAuthService(
            session=session,
            oauth_account_repo=oauth_account_repo,
            oauth_state_repo=oauth_state_repo,
            user_repo=user_repo,
            google_oauth_client=google_oauth_client,
            token_service=token_service,
        )
