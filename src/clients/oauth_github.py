from urllib.parse import urlencode

import httpx

from src.dtos.auth import OAuthUserInfoDTO
from src.exceptions.oauth import OAuthCodeExchangeError, OAuthProviderUnavailable, OAuthValidationError


class GitHubOAuthClient:
    AUTHORIZATION_ENDPOINT = 'https://github.com/login/oauth/authorize'
    TOKEN_ENDPOINT = 'https://github.com/login/oauth/access_token'
    SUB_INFO_ENDPOINT = 'https://api.github.com/user'
    EMAIL_INFO_ENDPOINT = 'https://api.github.com/user/emails'
    SCOPE = 'user:email'
    CODE_CHALLENGE_METHOD = 'S256'

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 redirect_uri: str,
                 httpx_client: httpx.AsyncClient):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._httpx_client = httpx_client

    def authorization_url(self, state: str, code_challenge: str) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": self.SCOPE,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": self.CODE_CHALLENGE_METHOD,
        }
        return f"{self.AUTHORIZATION_ENDPOINT}?{urlencode(params)}"

    async def _token_exchange(self, code: str, code_verifier: str) -> str:
        """
        Гит хаб возвращает сразу аксcес токен
        В отличии от гула, он юзает чисто оаутх протокол без oidc
        """
        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "code": code,
            "redirect_uri": self._redirect_uri,
            "code_verifier": code_verifier,
        }

        try:
            headers = {"Accept": "application/json"}
            response = await self._httpx_client.post(self.TOKEN_ENDPOINT, data=data, headers=headers)
            response.raise_for_status()
            token = response.json()
            error = token.get("error")
            if error:
                raise OAuthCodeExchangeError(token.get("error_description"))
            return token["access_token"]
        except httpx.HTTPStatusError as err:
            raise OAuthCodeExchangeError(str(err)) from err
        except httpx.RequestError as err:
            raise OAuthProviderUnavailable(str(err)) from err

    async def _fetch_profile(self, access_token: str) -> OAuthUserInfoDTO:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
        try:
            sub_info = await self._httpx_client.get(
                self.SUB_INFO_ENDPOINT,
                headers=headers,
            )
            email_info = await self._httpx_client.get(
                self.EMAIL_INFO_ENDPOINT,
                headers=headers,
            )

            user_data = sub_info.raise_for_status().json()
            emails = email_info.raise_for_status().json()

            sub = str(user_data["id"])

            primary_email = next((item for item in emails if item["primary"]), None)

            email = None
            verified = False

            if primary_email:
                email = primary_email["email"]
                verified = primary_email["verified"]
            data = {
                "sub": sub,
                "email": email,
                "email_verified": verified,
            }

            return OAuthUserInfoDTO(**data)
        except httpx.RequestError as err:
            raise OAuthProviderUnavailable(str(err)) from err
        except httpx.HTTPStatusError as err:
            raise OAuthValidationError(str(err)) from err

    async def get_user_info(self, code: str, code_verifier: str) -> OAuthUserInfoDTO:
        access_token = await self._token_exchange(code, code_verifier)
        return await self._fetch_profile(access_token)
