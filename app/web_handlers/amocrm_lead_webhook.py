from aiohttp import web
from loguru import logger
from multidict import MultiDictProxy

from app.cache.global_cache import lead_cache
from app.constants import amocrm_subdomain, GOOGLE_SHEET_ID, GOOGLE_WORKSHEET_NAME
from app.external_api.amo_crm import amo_custom_fields
from app.external_api.google_sheets import GoogleSheetsClient
from app.services.google_sheets_integration import GoogleSheetsService

amocrm_lead_webhook_app = web.Application()

client = GoogleSheetsClient()
gservice = GoogleSheetsService(client, GOOGLE_SHEET_ID, GOOGLE_WORKSHEET_NAME)


def find_key_by_value(d: MultiDictProxy, value):
    for k, v in d.items():
        if v == value:
            return k
    return None


async def webhook(request: web.Request) -> web.Response:
    multipart_data = await request.post()
    logger.info(f"Lead received {multipart_data}")
    account_subdomain = multipart_data.get('account[subdomain]')
    if account_subdomain != amocrm_subdomain:
        return web.Response(status=403)
    lead_id = multipart_data.get('leads[update][0][id]')

    if await lead_cache.is_ignored(lead_id, "amocrm"):
        logger.info("Lead update from AMOCRM ignored, GS is Editing now")
        return web.Response()
    await lead_cache.ignore(lead_id, "amocrm")
    status_id = multipart_data.get('leads[update][0][status_id]')
    price = multipart_data.get('leads[update][0][price]')
    lead_data = {
        "price": price,
        "status_id": status_id,
        "Comment": "",
        "Phone": "",
        "Email": ""
    }

    for k, _ in amo_custom_fields.items():
        key_str = find_key_by_value(multipart_data, k)
        if key_str:
            value_from_key = f'{key_str[:-6]}[values][0][value]'
            value = multipart_data.get(value_from_key)
            lead_data[k] = value
    gservice.update_user_by_key(lead_id, lead_data)
    return web.Response()


# async def process_offer_amocrm(lead_id):
#     logger.info(f"amocrm_stage_webhook.process_offer_amocrm {lead_id}")
#     amocrm_api = AmoCRM()
#     lead = await amocrm_api.get_lead(amo_crm_id=lead_id)
#     candidate = await Candidate().process_candidate_from_lead(lead)
#     hm_filter = {'id': candidate.hm_id} if candidate.hm_id else {'hm': candidate.hm}
#     hm_user = await User.filter(**hm_filter).first()
#
#
amocrm_lead_webhook_app.add_routes([web.post("/webhook", webhook)])
