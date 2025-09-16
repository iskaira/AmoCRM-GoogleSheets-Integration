class LeadIgnoreCache:
    def __init__(self, redis_client, redis_key="ignore_leads", ttl=5):
        self.redis_client = redis_client
        self.redis_key = redis_key
        self.ttl = ttl

    async def is_ignored(self, lead_id):
        lead_id = str(lead_id)
        ignored = await self.redis_client.redis.sismember(self.redis_key, lead_id)
        print(f"[is_ignored] lead_id={lead_id}, ignored={ignored}")
        return ignored

    async def ignore(self, lead_id):
        lead_id = str(lead_id)
        await self.redis_client.redis.sadd(self.redis_key, lead_id)
        await self.redis_client.redis.expire(self.redis_key, self.ttl)
        current = await self.redis_client.redis.smembers(self.redis_key)
        print(f"[ignore] added lead_id={lead_id}, current set={current}")
