import os

from aiohttp import ClientSession
from dotenv import load_dotenv

from DATABASE.database import db

load_dotenv()


class HTTPClient:
    def __init__(self, base_url: str):
        self._session = ClientSession(
            base_url=base_url
        )
        self._closed = False

    async def close(self):
        if not self._closed:
            await self._session.close()
            self._closed = True


class VKHTTPClient(HTTPClient):
    async def get_code(self, code: str, code_verifier: str, device_id: str, state: str):
        params = {
            'grant_type': 'authorization_code',
            'code_verifier': code_verifier,
            'redirect_uri': os.getenv('BASE_URL') + '/api/v1/vk/auth',
            'code': code,
            'client_id': os.getenv('VK_APP_ID'),
            'device_id': device_id,
            'state': state,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with self._session.post("/oauth2/auth", data=params, headers=headers) as response:
            result = await response.json()
            if 'access_token' in result:
                return {"ok": True, "access_token": result['access_token'],
                        'refresh_token': result['refresh_token'],
                        'msg': None}
            else:
                return {"ok": False, "error": result['error'], 'msg': result}

    async def refresh(self, state: str, token: str):
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': db.query(query='SELECT vk_refresh_token FROM tokens WHERE vk_token=%s', values=(token,), fetch='fetchone')[0],
            'client_id': os.getenv('VK_APP_ID'),
            'device_id': db.query(query='SELECT vk_device_id FROM tokens WHERE vk_token=%s', values=(token,), fetch='fetchone')[0],
            'state': state,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with self._session.post("/oauth2/auth", data=params, headers=headers) as response:
            result = await response.json()
            if 'access_token' in result:
                return {"ok": True, "access_token": result['access_token'], 'refresh_token': result['refresh_token'],
                        'device_id': result['device_id'], 'msg': None}
            else:
                return {"ok": False, "error": result['error'], 'msg': {'description': result['error_description'], 'state': result['state']}}



class YandexHTTPClient(HTTPClient):
    async def get_code(self, code_verifier: str, code: str, client_id: str):
        params = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'code': code,
            'code_verifier': code_verifier,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with self._session.post("/token", data=params, headers=headers) as response:
            result = await response.json()
            if 'access_token' in result:
                return {"ok": True, "access_token": result['access_token'], 'refresh_token': result['refresh_token'],
                        'msg': None}
            else:
                return {"ok": False, "error": result['error'],
                        'msg': {'description': result['error_description'], 'state': result['state']}}

    async def refresh_code(self, token: str):
        params = {
            'grant_type': 'refresh_token',
            'client_id': os.getenv('YANDEX_APP_ID'),
            'code': os.getenv('YANDEX_APP_SECRET'),
            'refresh_token': db.query(query='SELECT yandex_refresh_token FROM tokens WHERE yandex_token=%s',
                                      values=(token,), fetch='fetchone')[0]
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with self._session.post("/token", data=params, headers=headers) as response:
            result = await response.json()
            if 'access_token' in result:
                return {"ok": True, "access_token": result['access_token'], 'refresh_token': result['refresh_token'],
                        'msg': None}
            else:
                return {"ok": False, "error": result['error'],
                        'msg': {'description': result['error_description'], 'state': result['state']}}

