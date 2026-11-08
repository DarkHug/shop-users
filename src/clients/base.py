from typing import Protocol

from src.dtos.auth import OAuthUserInfoDTO


class OAuthClient(Protocol):
    def authorization_url(self, state: str, code_challenge: str) -> str:
        ...

    async def get_user_info(self, code: str, code_verifier: str) -> OAuthUserInfoDTO:
        ...