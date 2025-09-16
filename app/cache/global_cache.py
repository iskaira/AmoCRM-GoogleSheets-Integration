from app.cache.lead_ignore_cache import LeadIgnoreCache
from app.cache.redis_client import RedisClient
from app.constants import REDIS_URL

redis_client: RedisClient | None = None
lead_cache: LeadIgnoreCache | None = None


async def init_cache(redis_url: str = REDIS_URL, ttl: int = 5):
    global redis_client, lead_cache
    if redis_client is None:
        redis_client = RedisClient(redis_url)
        lead_cache = LeadIgnoreCache(redis_client, ttl=ttl)
    await redis_client.connect()
    return redis_client, lead_cache
