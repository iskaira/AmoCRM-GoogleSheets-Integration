__all__ = ["app_factory"]

from typing import Dict

from aiohttp import web

from app.cache.global_cache import redis_client
from app.cache.lead_ignore_cache import LeadIgnoreCache
from app.cache.redis_client import RedisClient
from app.constants import REDIS_URL


def app_factory(
    app: web.Application,
) -> web.Application:
    from .web_handlers import google_sheets_app, amocrm_lead_webhook_app
    from app.external_api.google_sheets import GoogleSheetsClient
    from app.services.google_sheets_integration import GoogleSheetsService

    sub_apps: Dict[str, web.Application] = {
        "/gsheets": google_sheets_app,
        '/amocrm_lead': amocrm_lead_webhook_app
    }

    for prefix, sub_app in sub_apps.items():
        app.add_subapp(prefix, sub_app)
    return app
