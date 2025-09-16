import logging

from app.cache.global_cache import lead_cache
from app.services.amo_integration import add_or_update_lead

logger = logging.getLogger(__name__)

async def lead_queue_handler(lead_id: str, source: str, payload: dict):
    """
    Выполняется в воркере для каждого события.
    - проверяем еще раз is_ignored (direction-aware)
    - продлеваем ignore для текущего source перед обработкой
    - вызываем add_or_update_lead
    """
    # payload contains row and user_data
    row = payload.get("row")
    user_data = payload.get("user_data", {})

    # если есть внешний флаг запрещающий обработку (opposite source active) — пропускаем
    if await lead_cache.is_ignored(lead_id, source):
        logger.info(f"Skipping lead {lead_id} from {source} because opposite source is active")
        return

    # продлеваем ignore на время обработки, чтобы противоположный источник не вмешался
    await lead_cache.ignore(lead_id, source)

    try:
        logger.info(f"Worker processing lead {lead_id} from {source} row={row}")
        await add_or_update_lead(row, user_data)
        logger.info(f"Worker finished lead {lead_id}")
    except Exception:
        logger.exception(f"Error processing lead {lead_id}")
        raise
