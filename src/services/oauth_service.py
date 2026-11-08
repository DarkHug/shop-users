from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.base import OAuthClient
from src.dtos.auth import TokenReturnDTO
from src.dtos.oauth import URLReturnDTO
from src.dtos.users import OAuthAccountCreateDBDTO
from src.dtos.users import UserOAuthCreateDBDTO
from src.exceptions.oauth import OAuthStateInvalid, OAuthEmailNotVerified
from src.models.oauth import Provider
from src.oauth_utils import generate_state, generate_pkce
from src.repos.oauth_account_repo import OAuthAccountRepository
from src.repos.oauth_state_repo import OAuthStateRepository
from src.repos.user_repo import UserRepository
from src.services.token_service import TokenService


class OAuthService:
    def __init__(
            self,
            session: AsyncSession,
            oauth_account_repo: OAuthAccountRepository,
            oauth_state_repo: OAuthStateRepository,
            user_repo: UserRepository,
            clients: dict[Provider, OAuthClient],
            token_service: TokenService,
    ):
        self._session = session
        self._oauth_account_repo = oauth_account_repo
        self._oauth_state_repo = oauth_state_repo
        self._user_repo = user_repo
        self._clients = clients
        self._token_service = token_service

    async def get_authorization_url(self, provider: Provider) -> URLReturnDTO:
        state = generate_state()
        pkce = generate_pkce()
        client = self._clients[provider]
        await self._oauth_state_repo.save(provider, state, pkce.verifier)
        return URLReturnDTO(url=client.authorization_url(state, pkce.challenge))

    async def login(self, provider: Provider, code: str, state: str) -> TokenReturnDTO:
        verifier = await self._oauth_state_repo.get_and_delete(provider, state)
        client = self._clients[provider]
        if verifier is None:
            raise OAuthStateInvalid
        user_info = await client.get_user_info(code, verifier)

        if not user_info.email_verified or user_info.email is None:
            raise OAuthEmailNotVerified

        oauth_account = await self._oauth_account_repo.get_account(provider, user_info.sub)
        if oauth_account:
            user_id = oauth_account.user_id
        else:
            main_account = await self._user_repo.get_by_email(user_info.email)
            if main_account:
                user_id = main_account.id
            else:
                new_user = await self._user_repo.create(UserOAuthCreateDBDTO(email=user_info.email))
                user_id = new_user.id

            data = OAuthAccountCreateDBDTO(sub=user_info.sub, provider=provider, user_id=user_id)
            await self._oauth_account_repo.create(data)

        token = await self._token_service.create_token_pair(user_id)
        await self._session.commit()
        return token
