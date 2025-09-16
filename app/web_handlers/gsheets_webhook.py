from aiohttp import web
from loguru import logger
from app.cache.global_cache import lead_cache


from app.services.amo_integration import add_or_update_lead

google_sheets_app = web.Application()


async def handle_webhook(request: web.Request):
    data = await request.json()
    logger.info(f"Webhook data from Google Sheets: {data}")

    row_number = data.get("row")
    values = data.get("data", [])
    if not values or len(values) < 5:
        return web.json_response({"status": "error", "reason": "invalid_data"})

    phone = values[0]
    email = values[1]
    price = values[2] or 0
    comment = values[3]
    lead_id = str(values[4]) if values[4] is not None else ""

    if not (phone and email and str(price).isdigit()):
        logger.error("Missing/invalid fields")
        return web.json_response({"status": "error", "row": row_number})

    user_data = {"phone": phone, "email": email, "price": int(price), "comment": comment, "lead_id": lead_id}

    if await lead_cache.is_ignored(lead_id, "gsheets"):
        logger.info(f"Lead {lead_id} ignored for gsheets (AMO action in progress)")
        return web.json_response({"status": "ignored", "row": row_number})

    await lead_cache.ignore(lead_id, "gsheets")

    await request.app["lead_queue"].enqueue(
        "gsheets",
        row_number,
        user_data,
    )

    logger.info(f"Lead {lead_id} enqueued (gsheets)")
    return web.json_response({"status": "queued", "row": row_number})


google_sheets_app.add_routes([web.post("/webhook", handle_webhook)])
