import asyncio
from datetime import datetime

from aiohttp import web

from app.cache.global_cache import init_cache

uptime_now = datetime.now()

app = web.Application()


loop = asyncio.get_event_loop()
loop.run_until_complete(init_cache())


def setup():
    ...
