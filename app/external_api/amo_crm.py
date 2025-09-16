import dataclasses
from typing import Optional, List

import aiohttp
from loguru import logger

from app.constants import (LEAD_PHONE_ID, LEAD_EMAIL_ID, LEAD_COMMENT_ID,
                           ACCESS_TOKEN, amo_crm_link)
from app.external_api import API, get_session

DEFAULT_LIMIT = 50


amo_custom_fields = {
    "Email": LEAD_EMAIL_ID,
    "Phone": LEAD_PHONE_ID,
    "Comment": LEAD_COMMENT_ID,
}


@dataclasses.dataclass
class CustomFieldEnums:
    id: int
    name: str


async def compare_email(custom_fields, email):
    correct_email_found = False
    if custom_fields:
        for field in custom_fields:
            if field.get('field_id') == amo_custom_fields.get("Email"):
                field_value = field.get('values') if field.get('values') else []
                value = field_value[0]['value'] if len(field_value) > 0 else ''
                logger.info(f"Email {value} found - {email} provided")
                if value and value.lower() == email.lower():
                    logger.info(f"{email} Found")
                    correct_email_found = True
                    break
    return correct_email_found


class AmoCRM(API):
    base_path = amo_crm_link
    token = ACCESS_TOKEN

    @get_session
    async def account(self, session: aiohttp.ClientSession):
        async with session.get(
            self.get_full_path('/api/v2/account'),
            headers=self.get_headers()
        ) as response:
            return response.ok

    @get_session
    async def get_lead(
        self,
        session: aiohttp.ClientSession,
        amo_crm_id: int
    ) -> Optional[dict]:
        async with session.get(
            self.get_full_path(f"/api/v4/leads/{amo_crm_id}?with=contacts"),
            headers=self.get_headers()
        ) as response:
            if response.status == 204:
                return
            if response.ok:
                return await response.json()

    @get_session
    async def create_lead(self, session: aiohttp.ClientSession,
                          json_data: List[dict]):
        logger.info(f'{json_data}')
        async with session.post(
            self.get_full_path('/api/v4/leads/complex'),
            headers=self.get_headers(),
            json=json_data
        ) as resp:
            data = {}
            if not resp.ok:
                logger.error(resp.status)
                logger.error(resp.content)
            if resp.ok:
                data = await resp.json()
            return data

    @get_session
    async def update_lead(
        self,
        session: aiohttp.ClientSession,
        amo_crm_id: int,
        new_data
    ):
        async with session.patch(
            self.get_full_path(f"/api/v4/leads/{amo_crm_id}"),
            json=new_data,
            headers=self.get_headers()
        ) as response:
            if not response.ok:
                logger.error(response.reason)
                logger.error(f"PATCH /api/v4/leads/{amo_crm_id}, {response.status}")
                logger.error(new_data)
            logger.info(await response.json())
            return response.ok

    @get_session
    async def get_leads_by_email(
        self,
        session: aiohttp.ClientSession,
        email: str
    ) -> Optional[list]:
        async with session.get(
            self.get_full_path(f"/api/v4/leads?query={email}"),
            headers=self.get_headers()
        ) as resp:
            new_leads = []
            if resp.ok:
                if resp.status == 200:
                    data = await resp.json()
                    leads = data['_embedded']['leads']
                    logger.info('got leads, checking for correct email')
                    for lead in leads:
                        logger.info(f'{lead["id"]}')
                        email_is_ok = await compare_email(lead['custom_fields_values'],
                                                          email)
                        if email_is_ok:
                            new_leads.append(lead)
            logger.info(new_leads)
            return new_leads

    @get_session
    async def get_custom_fields_by_id_json(
        self,
        session: aiohttp.ClientSession,
        field_id: int
    ) -> Optional[dict]:
        async with session.get(
            self.get_full_path(f"/api/v4/leads/custom_fields/{field_id}"),
            headers=self.get_headers()
        ) as resp:
            if resp.status == 204:
                return
            if resp.ok:
                return await resp.json()

    @get_session
    async def update_custom_fields_by_id(
        self,
        session: aiohttp.ClientSession,
        field_id: int,
        json_data: dict,
        entity: str = 'leads'
    ) -> Optional[dict]:
        async with session.patch(
            self.get_full_path(f"/api/v4/{entity}/custom_fields/{field_id}"),
            json=json_data,
            headers=self.get_headers()
        ) as resp:
            if resp.status == 204:
                return {}
            if resp.ok:
                return await resp.json()
