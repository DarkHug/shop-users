from sqlalchemy.ext.asyncio import AsyncSession

from src.dtos.auth import TokenReturnDTO
from src.dtos.users import OAuthAccountCreateDBDTO
from src.dtos.users import UserOAuthCreateDBDTO
from src.exceptions.oauth import OAuthStateInvalid, OAuthEmailNotVerified
from src.models.oauth import Provider
from src.oauth_utils import generate_state, generate_pkce
from src.repos.oauth_account_repo import OAuthAccountRepository
from src.repos.oauth_state_repo import OAuthStateRepository
from src.repos.user_repo import UserRepository
from src.services.oauth_google import GoogleOAuthClient
from src.services.token_service import TokenService


class GoogleAuthService:
    def __init__(
            self,
            session: AsyncSession,
            oauth_account_repo: OAuthAccountRepository,
            oauth_state_repo: OAuthStateRepository,
            user_repo: UserRepository,
            google_oauth_client: GoogleOAuthClient,
            token_service: TokenService,
    ):
        self._session = session
        self._oauth_account_repo = oauth_account_repo
        self._oauth_state_repo = oauth_state_repo
        self._user_repo = user_repo
        self._google_oauth_client = google_oauth_client
        self._token_service = token_service

    async def get_authorization_url(self) -> str:
        state = generate_state()
        pkce = generate_pkce()
        await self._oauth_state_repo.save(state, pkce.verifier)
        return self._google_oauth_client.authorization_url(state, pkce.challenge)

    async def login(self, code: str, state: str) -> TokenReturnDTO:
        verifier = await self._oauth_state_repo.get_and_delete(state)
        if verifier is None:
            raise OAuthStateInvalid
        id_token = await self._google_oauth_client.token_exchange(code=code, code_verifier=verifier)
        user_info = self._google_oauth_client.check_id_token(id_token)
        if not user_info.email_verified:
            raise OAuthEmailNotVerified

        oauth_account = await self._oauth_account_repo.get_account(Provider.GOOGLE, user_info.sub)
        if oauth_account:
            user_id = oauth_account.user_id
        else:
            main_account = await self._user_repo.get_by_email(user_info.email)
            if main_account:
                user_id = main_account.id
            else:
                new_user = await self._user_repo.create(UserOAuthCreateDBDTO(email=user_info.email))
                user_id = new_user.id

            data = OAuthAccountCreateDBDTO(sub=user_info.sub, provider=Provider.GOOGLE, user_id=user_id)
            await self._oauth_account_repo.create(data)

        token = await self._token_service.create_token_pair(user_id)
        await self._session.commit()
        return token
