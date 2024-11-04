import json

from DATABASE.redis_client import redis_client as redis
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from SERVER.Utils.VKHTTPClient import VKHTTPClient

router = APIRouter(prefix="/webhook/vk", tags=["vk_webhook"])


@router.get("/callback")
async def vk_callback(request: Request):
    client = VKHTTPClient("https://id.vk.com")

    code = request.query_params.get('code')
    state = request.query_params.get('state')
    device_id = request.query_params.get('device_id')

    pkce_json = redis.get(f'pkce:{state}')

    if not pkce_json:
        raise HTTPException(status_code=400, detail="Invalid state or PKCE data not found")

    pkce_data = json.loads(pkce_json.decode('utf-8'))
    try:
        result = await client.get_code(code=code, code_verifier=pkce_data['verifier'], device_id=device_id, state=state)
        redis.delete(f'pkce:{state}')
        redis.set('vk_token', result['access_token'])
    finally:
        await client.close()
    return RedirectResponse(f"http://localhost:5173/api/vk-login/state?status={result['ok']}&msg={result['msg']}")