import os
from dotenv import load_dotenv

from SERVER.Utils.HTTPClient import HTTPClient

load_dotenv()

class VKHTTPClient(HTTPClient):
    async def get_code(self, code: str, code_verifier: str, device_id: str, state: str):
        params = {
            'grant_type': 'authorization_code',
            'code_verifier': code_verifier,
            'redirect_uri': os.getenv('BASE_URL')+'/webhook/vk/callback',
            'code': code,
            'client_id': os.getenv('VK_APP_ID'),
            'device_id': device_id,
            'state': state,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        async with self._session.post("/oauth2/auth", data=params, headers=headers) as response:
            result = await response.json()
        if 'access_token' in result:
            return {"ok": True, "access_token": result['access_token'], 'msg': None}
        else:
            return {"ok": False, "error": "Failed to get access token", 'msg': result}
