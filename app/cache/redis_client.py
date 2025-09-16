import redis.asyncio as redis


class RedisClient:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: redis.Redis | None = None

    async def connect(self):
        self.redis = redis.from_url(self.redis_url, decode_responses=True)

    async def aclose(self):
        if self.redis:
            await self.redis.aclose()
            await self.redis.connection_pool.disconnect()
