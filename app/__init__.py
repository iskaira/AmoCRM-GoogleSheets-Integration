__all__ = ["app_factory"]

import asyncio
from typing import Dict

from aiohttp import web
from loguru import logger

from app.cache.global_cache import redis_client
from app.cache.lead_ignore_cache import LeadIgnoreCache
from app.cache.lead_queue import LeadQueue
from app.cache.redis_client import RedisClient
from app.constants import REDIS_URL
from app.services.amo_integration import add_or_update_lead


async def start_lead_worker(app: web.Application):
    """
    Запускает фонового воркера для обработки задач из Redis Streams.
    """

    queue = app["lead_queue"]

    async def handler(source: str, row_number: int, user_data: dict):
        """
        Обработчик задачи из очереди.
        """
        try:
            logger.info(f"[LeadWorker] Handling task from {source}: row={row_number}, data={user_data}")
            await add_or_update_lead(row_number, user_data)
        except Exception as e:
            logger.exception(f"[LeadWorker] Ошибка при обработке задачи: {e}")

    # Запускаем воркер как отдельную задачу
    app["lead_worker_task"] = asyncio.create_task(queue.worker(handler))


async def close_lead_worker(app: web.Application):
    """
    Аккуратно останавливает фонового воркера.
    """
    task = app.get("lead_worker_task")
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("[LeadWorker] Task cancelled")

    # Закрываем соединение с Redis
    if "lead_queue" in app:
        await app["lead_queue"].aclose()



def app_factory(
    app: web.Application,
) -> web.Application:
    from .web_handlers import google_sheets_app, amocrm_lead_webhook_app
    from app.external_api.google_sheets import GoogleSheetsClient
    from app.services.google_sheets_integration import GoogleSheetsService

    lead_queue = LeadQueue()
    app["lead_queue"] = lead_queue
    app.on_startup.append(lambda app: lead_queue.connect())
    app.on_startup.append(start_lead_worker)
    app.on_cleanup.append(close_lead_worker)

    sub_apps: Dict[str, web.Application] = {
        "/gsheets": google_sheets_app,
        '/amocrm_lead': amocrm_lead_webhook_app
    }

    for prefix, sub_app in sub_apps.items():
        sub_app['lead_queue'] = lead_queue
        app.add_subapp(prefix, sub_app)
    return app
