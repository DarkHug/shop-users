from redis.asyncio import Redis
from src.models.oauth import Provider as OAuthProvider

class OAuthStateRepository:
    PREFIX = "oauth_state:"

    def __init__(self, redis: Redis, ttl: int):
        self._redis = redis
        self._ttl = ttl

    def _key(self, provider: OAuthProvider, state: str) -> str:
        return f"{self.PREFIX}{provider}:{state}"

    async def save(self, provider: OAuthProvider, state: str, code_verifier: str) -> None:
        await self._redis.set(self._key(provider, state), code_verifier, ex=self._ttl)

    async def get_and_delete(self, provider: OAuthProvider, state: str) -> str | None:
        raw = await self._redis.getdel(self._key(provider, state))
        if raw is None:
            return None
        return raw.decode()
