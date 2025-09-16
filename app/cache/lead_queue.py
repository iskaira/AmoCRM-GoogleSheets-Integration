import asyncio
import json
import redis.asyncio as redis
from loguru import logger


class LeadQueue:
    def __init__(self, redis_url="redis://localhost", stream_key="lead_stream"):
        self.redis_url = redis_url
        self.stream_key = stream_key
        self.redis = None

    async def connect(self):
        """Подключаемся к Redis"""

        if not self.redis:
            self.redis = await redis.from_url(
                self.redis_url,
                decode_responses=True,
            )
            await self.redis.delete("lead_stream")

    async def aclose(self):
        """Закрываем соединение"""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def enqueue(self, source: str, row_number: int, user_data: dict):
        """Добавляем задачу в Redis Stream"""
        await self.redis.xadd(
            self.stream_key,
            {
                "source": source,
                "row_number": str(row_number),
                "data": json.dumps(user_data or {}),
            },
        )

    async def worker(self, handler):
        last_id = "0-0"
        while True:
            try:
                resp = await self.redis.xread(
                    {self.stream_key: last_id},
                    block=5000,
                    count=1,
                )
                if not resp:
                    continue

                for stream, messages in resp:
                    for msg_id, fields in messages:
                        try:
                            source = fields.get(b"source") or fields.get("source")
                            row_number = fields.get(b"row_number") or fields.get("row_number")
                            data_raw = fields.get(b"data") or fields.get("data")

                            if isinstance(source, bytes):
                                source = source.decode()
                            if isinstance(row_number, bytes):
                                row_number = row_number.decode()
                            if isinstance(data_raw, bytes):
                                data_raw = data_raw.decode()

                            user_data = json.loads(data_raw) if data_raw else {}

                            logger.info(
                                f"[LeadQueue] Got task {msg_id}: "
                                f"source={source}, row={row_number}, data={user_data}"
                            )

                            await handler(source, int(row_number), user_data)
                            last_id = msg_id
                        except Exception as e:
                            logger.exception(f"[LeadQueue] Ошибка при обработке {msg_id}: {e}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"[LeadQueue] Worker loop error: {e}")
                await asyncio.sleep(1)
