import aiohttp


def get_session(handler):
    async def wrapper(self, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            return await handler(self, session, *args, **kwargs)

    return wrapper


class API:
    base_path = ''
    token = ''

    def get_auth_header(self):
        return {
            'Authorization': f'Bearer {self.token}'
        }

    def get_headers(self, headers=None):
        if headers is None:
            headers = {}
        return {
            **self.get_auth_header(),
            **headers,
        }

    def get_full_path(self, path):
        return self.base_path + path
