import json
import os

from fastapi import APIRouter, status, Response
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from DATABASE.database import db
from DATABASE.redis_client import RedisClient
from LOGGING_SETTINGS.settings import server_logger
from SERVER.Utils.HTTPClients import YandexHTTPClient

router = APIRouter(prefix="/api/yandex", tags=["Yandex services"])


class YandexAuthSchema(BaseModel):
    code: int = Field(default=..., title="", description="Verification code", examples=['123456'])
    state: str = Field(default=..., title="", description="Verification state string",
                       examples=['ebf2b96ac0d81fdad06aa74447jkku4e'], min_length=32, max_length=32)


class YandexAuthResponse200Schema(BaseModel):
    ok: bool = Field(title="", default=True, description='Operation status', examples=[True])
    token: str = Field(title="", description='Yandex access token', examples=['<access_token>'])
    refresh_token: str = Field(title="", description='Yandex refresh token', examples=['<refresh_token>'])


class YandexAuthResponseErrorSchema(BaseModel):
    ok: bool = Field(title="", default=False, description='Operation status')
    error: str = Field(title='', description="Description of error")
    msg: str = Field(title='', description="Message of error")


description_auth = """
Method for Yandex authentication
"""

responses = {
    200: {"model": YandexAuthResponse200Schema, "description": "Yandex Auth success"},
    400: {"model": YandexAuthResponseErrorSchema, "description": "PKCE data not found"},
    401: {"model": YandexAuthResponseErrorSchema, "description": "Invalid secret code"},
    500: {"model": YandexAuthResponseErrorSchema, "description": "Yandex Auth failed"},
}


@router.get("/auth", status_code=status.HTTP_200_OK, response_model=YandexAuthResponse200Schema,
            responses=responses, description=description_auth)
async def auth(data: YandexAuthSchema, response: Response):
    redis = RedisClient()
    client = YandexHTTPClient("https://oauth.yandex.ru/")

    pkce_json = await redis.get(f'pkce:{data.state}')

    if not pkce_json:
        server_logger.warn(f'Invalid state or PKCE data not found | {data.state}')
        response.status_code = status.HTTP_400_BAD_REQUEST
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'ok': False,
                                                                              'error': f'Invalid state or PKCE data not found',
                                                                              'msg': f'Invalid state or PKCE data not found | {data.state}'})

    pkce_data = json.loads(pkce_json.decode('utf-8'))
    try:
        result = await client.get_code(code=data.code, code_verifier=pkce_data['verifier'],
                                       client_id=os.getenv('YANDEX_APP_ID'))
        if result['ok']:
            await redis.delete(f'pkce:{data.state}')
            db.query(query='INSERT INTO tokens (yandex_token, yandex_refresh_token) VALUES (%s, %s)',
                     values=(result['access_token'], result['refresh_token']), msg='Error while insert yandex token')
            server_logger.info('Yandex token fetched successfully')
            response.status_code = status.HTTP_200_OK
            return YandexAuthResponse200Schema(ok=True, token=result['access_token'], refresh_token=result['refresh_token'])
        else:
            server_logger.warn(f'{result['error']} | {result['msg']}')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={'error': result['error'], 'msg': result['msg']})
    except Exception as _ex:
            server_logger.error(f'Yandex Auth failed with error | {_ex}')
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content={'error': 'Yandex Auth failed with error',
                                         'msg': str(_ex)})
    finally:
        await client.close()
        await redis.close()


class YandexRefreshSchema(BaseModel):
    token_old: str = Field(title="", description='Yandex old access token', examples=['<access_token>'])


description_refresh = """
Method for Yandex refresh token
"""

responses_refresh = {
    200: {"model": YandexAuthResponse200Schema, "description": "Yandex refresh success"},
    401: {"model": YandexAuthResponseErrorSchema, "description": "Invalid secret code"},
    500: {"model": YandexAuthResponseErrorSchema, "description": "Yandex refresh failed"},
}


@router.post('/refresh', response_model=YandexAuthResponse200Schema, responses=responses_refresh, description=description_refresh)
async def refresh_token(data: YandexRefreshSchema, response: Response):
    client = YandexHTTPClient("https://oauth.yandex.ru/")
    try:
        result = await client.refresh_code(token=data.token_old)
        if 'access_token' in result.keys():
            db.query(query="""BEGIN;
            UPDATE tokens SET yandex_refresh_token=%s WHERE yandex_token=%s;
            UPDATE tokens SET yandex_token=%s WHERE yandex_token=%s""",
                     values=(result['refresh_token'], data.token_old, result['access_token'], data.token_old),
                     msg='Error while update yandex token')
            response.status_code = status.HTTP_200_OK
            return YandexAuthResponse200Schema(ok=True, token=result['access_token'], refresh_token=result['refresh_token'])
        else:
            server_logger.warn(f'{result['error']} | {result['msg']}')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={'error': result['error'], 'msg': result['msg']})
    except Exception as _ex:
        server_logger.error(f'Failed to update yandex token - {_ex}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={'error': 'Yandex Refresh failed with error',
                                     'msg': str(_ex)})
    finally:
        await client.close()
