import asyncio
import base64
import hashlib
import secrets

import httpx
from clients.oauth_github import GitHubOAuthClient

CLIENT_ID = "Ov23liVRgKbTBqlj3f3P"
CLIENT_SECRET = "acd659398f83bf54529f550671a76a5dfc65e082"
REDIRECT_URI = "http://localhost:3000/auth/github/callback"


def generate_pkce():
    verifier = secrets.token_urlsafe(32)

    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()

    return verifier, challenge


async def main():
    async with httpx.AsyncClient() as http_client:
        github = GitHubOAuthClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            httpx_client=http_client,
        )

        state = secrets.token_urlsafe(32)
        verifier, challenge = generate_pkce()

        url = github.authorization_url(
            state=state,
            code_challenge=challenge,
        )

        print("Открой ссылку в браузере:")
        print(url)

        code = input("\nВставь authorization code: ")

        token = await github.token_exchange(
            code=code,
            code_verifier=verifier,
        )
        print(token)

        print("\nAccess Token успешно получен!")

        user_info = await github._fetch_profile(access_token=token)

        print("\nИнформация о пользователе:")
        print(user_info)


if __name__ == "__main__":
    asyncio.run(main())
