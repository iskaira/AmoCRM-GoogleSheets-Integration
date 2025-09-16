class LeadIgnoreCache:
    def __init__(self, redis_client, ttl: int = 5):
        self.redis_client = redis_client
        self.ttl = ttl

    def _make_key(self, lead_id: str | int, source: str) -> str:
        return f"ignore:lead:{lead_id}:{source}"

    async def ignore(self, lead_id: str | int, source: str):
        key = self._make_key(lead_id, source)
        await self.redis_client.redis.set(key, "1", ex=self.ttl)
        print(f"[ignore] set {key}")

    async def is_ignored(self, lead_id: str | int, source: str) -> bool:
        opposite = "amocrm" if source == "gsheets" else "gsheets"
        key = self._make_key(lead_id, opposite)
        exists = await self.redis_client.redis.exists(key)
        print(f"[is_ignored] lead_id={lead_id}, source={source}, opposite_key={key}, exists={exists}")
        return bool(exists)
