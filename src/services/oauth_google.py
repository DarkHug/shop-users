from urllib.parse import urlencode

import httpx
import jwt
from jwt import PyJWKClient

from src.dtos.auth import OAuthUserInfoDTO
from src.exceptions.oauth import OAuthProviderUnavailable, OAuthCodeExchangeError, OAuthValidationError


class GoogleOAuthClient:
    AUTHORIZATION_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
    SCOPE = 'openid email'
    RESPONSE_TYPE = 'code'
    CODE_CHALLENGE_METHOD = 'S256'
    GRANT_TYPE = 'authorization_code'
    TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
    JWKS_URI = 'https://www.googleapis.com/oauth2/v3/certs'
    ISSUERS = ('https://accounts.google.com', 'accounts.google.com')

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            redirect_uri: str,
            httpx_client: httpx.AsyncClient,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._httpx_client = httpx_client
        self._jwk_client = PyJWKClient(self.JWKS_URI)

    def authorization_url(self, state: str, code_challenge: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": self.RESPONSE_TYPE,
            "scope": self.SCOPE,
            "code_challenge": code_challenge,
            "code_challenge_method": self.CODE_CHALLENGE_METHOD,
            "state": state,
        }
        return f"{self.AUTHORIZATION_ENDPOINT}?{urlencode(params)}"

    async def token_exchange(self, code: str, code_verifier: str) -> str:
        """
        Возвращает id-token
        """
        data = {
            "grant_type": self.GRANT_TYPE,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "redirect_uri": self._redirect_uri,
            "code_verifier": code_verifier,
            "code": code,
        }

        try:
            response = await self._httpx_client.post(self.TOKEN_ENDPOINT, data=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data["id_token"]
        except httpx.HTTPStatusError as err:
            raise OAuthCodeExchangeError(err.response.text) from err
        except httpx.RequestError as err:
            raise OAuthProviderUnavailable(str(err)) from err

    def check_id_token(self, id_token: str) -> OAuthUserInfoDTO:
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(id_token).key
            data = jwt.decode(id_token,
                              key=signing_key,
                              algorithms=["RS256"],
                              audience=self._client_id,
                              issuer=self.ISSUERS,
                              )
            return OAuthUserInfoDTO(**data)
        except jwt.exceptions.PyJWTError as err:
            raise OAuthValidationError(str(err)) from err
