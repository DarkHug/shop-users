from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.oauth import OAuthEmailNotVerified
from src.dtos.auth import TokenReturnDTO
from src.dtos.oauth import URLReturnDTO
from src.exceptions.oauth import OAuthStateInvalid
from src.oauth_utils import generate_state, generate_pkce
from src.repos.oauth_account_repo import OAuthAccountRepository
from src.repos.oauth_state_repo import OAuthStateRepository
from src.repos.user_repo import UserRepository
from src.services.oauth_github import GitHubOAuthClient
from src.services.token_service import TokenService


class GithubAuthService:
    def __init__(self,
                 session: AsyncSession,
                 oauth_account_repo: OAuthAccountRepository,
                 oauth_state_repo: OAuthStateRepository,
                 user_repo: UserRepository,
                 github_oauth_client: GitHubOAuthClient,
                 token_service: TokenService
                 ):
        self._session = session
        self._oauth_account_repo = oauth_account_repo
        self._oauth_state_repo = oauth_state_repo
        self._user_repo = user_repo
        self._github_oauth_client = github_oauth_client
        self._token_service = token_service

    async def get_authorization_url(self) -> URLReturnDTO:
        state = generate_state()
        pkce = generate_pkce()
        await self._oauth_state_repo.save(state, pkce.verifier)
        return URLReturnDTO(url=self._github_oauth_client.authorization_url(state, pkce.challenge))

    async def login(self, code: str, state: str) -> TokenReturnDTO:
        verifier = await self._oauth_state_repo.get_and_delete(state)
        if verifier is None:
            raise OAuthStateInvalid
        user_token = await self._github_oauth_client.token_exchange(code, verifier)
        user_info = await self._github_oauth_client.get_user_info(user_token)
        if not user_info.email_verified:
            raise OAuthEmailNotVerified


