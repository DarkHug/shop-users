from redis.asyncio import Redis


class OAuthStateRepository:
    PREFIX = "oauth_state:"

    def __init__(self, redis: Redis, ttl: int):
        self._redis = redis
        self._ttl = ttl

    def _key(self, state: str) -> str:
        return self.PREFIX + state

    async def save(self, state: str, code_verifier: str) -> None:
        await self._redis.set(self._key(state), code_verifier, ex=self._ttl)

    async def get_and_delete(self, state: str) -> str | None:
        raw = await self._redis.getdel(self._key(state))
        if raw is None:
            return None
        return raw.decode()
