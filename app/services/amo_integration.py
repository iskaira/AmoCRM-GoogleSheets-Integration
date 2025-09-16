from loguru import logger

from app.constants import CREATE_STATUS_ID, CREATE_PIPELINE_ID, RESPONSIBLE_USER_ID, GOOGLE_SHEET_ID, \
    GOOGLE_WORKSHEET_NAME
from app.external_api.amo_crm import AmoCRM, amo_custom_fields
from app.external_api.google_sheets import GoogleSheetsClient
from app.services.google_sheets_integration import GoogleSheetsService

client = GoogleSheetsClient()
gservice = GoogleSheetsService(client, GOOGLE_SHEET_ID, GOOGLE_WORKSHEET_NAME)


async def add_or_update_lead(row_number, data):
    lead_id = None
    api = AmoCRM()
    email = data.get('email')
    price = int(data.get('price'))
    leads: [] = await api.get_leads_by_email(email)
    custom_fields = [
        {
            'field_id': amo_custom_fields.get("Email"),
            'values': [{
                'value': str(data.get('email'))
            }]
        },
        {
            'field_id': amo_custom_fields.get("Phone"),
            'values': [{
                'value': str(data.get('phone'))
            }]
        }
    ]
    if amo_custom_fields.get("Comment"):
        custom_fields.append({'field_id': amo_custom_fields.get("Comment"),
                              'values': [{'value': str(data.get('comment'))}]})

    if not leads:
        logger.info(f"no leads for email: {email}, creating new one...")
        json = [
            {
                "name": f"{data.get('phone')} {data.get('email')}",
                "status_id": CREATE_STATUS_ID,
                "price": price,
                "pipeline_id": CREATE_PIPELINE_ID,
                'responsible_user_id': RESPONSIBLE_USER_ID,
                "custom_fields_values": custom_fields,
                "_embedded": {
                    "companies": [],
                    "contacts": []
                }
            }
        ]
        res = await api.create_lead(json)
        if res:
            lead_id = res[0]['id']
            gservice.set_lead_status_for_row(lead_id=lead_id, status_id=CREATE_STATUS_ID, row_number=row_number)

        logger.info(f"Created lead {res}")
    if leads:
        lead = leads[-1]
        logger.info(lead)
        lead_id = lead['id']
        update_json = {
            "name": f"{data.get('phone')} {data.get('email')}",
            "price": price,
            "custom_fields_values": custom_fields
        }

        logger.info(update_json)
        res = await api.update_lead(lead_id, update_json)
        gservice.set_lead_status_for_row(row_number, lead_id=lead_id, status_id=lead['status_id'])
        logger.info(res)
    return lead_id
