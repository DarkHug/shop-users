from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.repos.user_repo import UserRepository
from src.services.password import PasswordHash
from src.services.user_service import UserService


class UserProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_repo(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

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
