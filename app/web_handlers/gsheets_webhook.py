from aiohttp import web
from loguru import logger
from app.cache.global_cache import lead_cache


from app.services.amo_integration import add_or_update_lead

google_sheets_app = web.Application()


async def handle_webhook(request: web.Request):
    data = await request.json()
    logger.info(data)
    logger.info(f"Получены данные из Google Sheets: {data}")

    row_number = data.get("row")
    values = data.get("data", [])
    user_data = {}
    phone = values[0]
    email = values[1]
    price = values[2] if values[2] else 0
    comment = values[3]
    lead_id = str(values[4])

    if phone and email and str(price).isdigit():
        user_data = {
            "phone": phone,
            "email": email,
            "price": price,
            "comment": comment
        }
    logger.info(user_data)
    if user_data:
        logger.info(f"Data prepared for processing amocrm: {user_data}")
        if await lead_cache.is_ignored(lead_id):
            logger.info("Lead update from GS ignored, AMOCRM is Editing now")
            return web.json_response({"status": "ok", "row": row_number})
        await lead_cache.ignore(lead_id)
        await add_or_update_lead(row_number, user_data)
    else:
        logger.error("Could not process data: required fields are missing or empty.")

    return web.json_response({"status": "ok", "row": row_number})


google_sheets_app.add_routes([web.post("/webhook", handle_webhook)])
