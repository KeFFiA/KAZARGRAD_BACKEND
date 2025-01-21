import json
import os

from fastapi import APIRouter, status, Response
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from DATABASE.database import db
from DATABASE.redis_client import RedisClient
from LOGGING_SETTINGS.settings import server_logger
from SERVER.Utils.HTTPClients import VKHTTPClient

router = APIRouter(prefix="/api/vk", tags=["VK services"])


class VKAuthSchema(BaseModel):
    code: int = Field(default=..., title="", description="Verification code", examples=['123456'])
    state: str = Field(default=..., title="", description="Verification state string",
                       examples=['ebf2b96ac0d81fdad06aa74447jkku4e'], min_length=32, max_length=32)
    device_id: str = Field(default=..., title="", description="Device ID", examples=['e312b4ffd5918206aa95e5747dcaee'])


class VKAuthResponse200Schema(BaseModel):
    ok: bool = Field(title="", default=True, description='Operation status', examples=[True])
    token: str = Field(title="", description='VK access token', examples=['<access_token>'])
    refresh_token: str = Field(title="", description='VK refresh token', examples=['<refresh_token>'])


class VKAuthResponseErrorSchema(BaseModel):
    ok: bool = Field(title="", default=False, description='Operation status')
    error: str = Field(title='', description="Description of error")
    msg: str = Field(title='', description="Message of error")


description_auth = """
Method for VK authentication
"""

responses = {
    200: {"model": VKAuthResponse200Schema, "description": "VK Auth success"},
    400: {"model": VKAuthResponseErrorSchema, "description": "PKCE data not found"},
    401: {"model": VKAuthResponseErrorSchema, "description": "Invalid secret code"},
    500: {"model": VKAuthResponseErrorSchema, "description": "VK Auth failed"},
}


@router.get("/auth", status_code=status.HTTP_200_OK, response_model=VKAuthResponse200Schema,
            description=description_auth, responses=responses)
async def auth(data: VKAuthSchema, response: Response):
    redis = RedisClient()
    client = VKHTTPClient("https://id.vk.com")

    pkce_json = await redis.get(f'pkce:{data.state}')

    if not pkce_json:
        server_logger.warn(f'Invalid state or PKCE data not found | {data.state}')
        response.status_code = status.HTTP_400_BAD_REQUEST
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'ok': False,
                                                                              'error': f'Invalid state or PKCE data not found',
                                                                              'msg': f'Invalid state or PKCE data not found | {data.state}'})

    pkce_data = json.loads(pkce_json.decode('utf-8'))
    try:
        result = await client.get_code(code=data.code, code_verifier=pkce_data['verifier'], device_id=data.device_id,
                                       state=data.state)
        if result['ok']:
            await redis.delete(f'pkce:{data.state}')
            db.query(query='INSERT INTO tokens (vk_token, vk_refresh_token, vk_device_id) VALUES (%s, %s, %s)',
                     values=(result['access_token'], result['refresh_token'], result['device_id']),
                     msg='Error while insert VK token')
            server_logger.info('VK token fetched successfully')
            response.status_code = status.HTTP_200_OK
            return VKAuthResponse200Schema(ok=True, token=result['access_token'], refresh_token=result['refresh_token'])
        else:
            server_logger.warn(f'{result['error']} | {result['msg']}')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={'ok': False, 'error': result['error'], 'msg': result['msg']})
    except Exception as _ex:
        server_logger.error(f'VK Auth failed with error | {_ex}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={'ok': False, 'error': f'VK Auth failed with error', 'msg': str(_ex)})
    finally:
        await client.close()
        await redis.close()
    # return RedirectResponse(f"https://kazargrad.tw1.ru/api/vk-login/state?status={result['ok']}&msg={result['msg']}")


class VKRefreshSchema(BaseModel):
    token_old: str = Field(title="", description='VK old access token', examples=['<access_token>'])


description_refresh = """
Method for VK refresh token
"""

responses_refresh = {
    200: {"model": VKAuthResponse200Schema, "description": "VK refresh success"},
    401: {"model": VKAuthResponseErrorSchema, "description": "Invalid secret code"},
    500: {"model": VKAuthResponseErrorSchema, "description": "VK refresh failed"},
}


@router.post("/refresh", response_model=VKAuthResponse200Schema, description=description_refresh,
             responses=responses_refresh)
async def refresh_token(data: VKRefreshSchema, response: Response):
    client = VKHTTPClient("https://id.vk.com")

    try:
        state = os.urandom(16).hex()
        result = await client.refresh(state=state, token=data.token_old)
        if result['ok']:
            db.query(query="""BEGIN;
                        UPDATE tokens SET vk_refresh_token=%s WHERE vk_token=%s;
                        UPDATE tokens SET vk_token=%s WHERE vk_token=%s""",
                     values=(result['refresh_token'], data.token_old, result['access_token'], data.token_old),
                     msg='Error while update VK token')
            response.status_code = status.HTTP_200_OK
            return VKAuthResponse200Schema(ok=True, token=result['access_token'], refresh_token=result['refresh_token'])
        else:
            server_logger.warn(f'{result['error']} | {result['msg']}')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={'ok': False, 'error': result['error'], 'msg': result['msg']})
    except Exception as _ex:
        server_logger.error(f'Failed to update VK token - {_ex}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={'ok': False, 'error': 'VK refresh failed', 'msg': str(_ex)})
    finally:
        await client.close()
