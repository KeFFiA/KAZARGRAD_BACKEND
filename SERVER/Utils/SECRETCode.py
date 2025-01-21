import json
import os
import random

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import JSONResponse

from DATABASE.redis_client import RedisClient
from LOGGING_SETTINGS.settings import server_logger


async def generate():
    redis = RedisClient()
    code = random.randint(100000, 999999)
    state = os.urandom(16).hex()

    data = {'code': code, 'state': state}

    await redis.set(f'secret_code:{state}', json.dumps(data))
    await redis.close()

    return data


router = APIRouter()


class SecretCodeResponse200Schema(BaseModel):
    ok: bool = Field(default=True, title="", description='Operation status')
    code: int = Field(default=..., title='', description='Verification code', examples=['123456'])
    state: str = Field(default=..., title='', description='Verification state string', examples=['ebf2b96ac0d5918206aa95e5747dcaee'], min_length=32, max_length=32)


class SecretCodeResponseErrorSchema(BaseModel):
    ok: bool = Field(title="", default=False, description="Operation status")
    error: str = Field(title='', description="Description of error")
    msg: str = Field(title='', description="Message of error")


description = """
Method for generating secret code
"""

responses = {
    200: {'model': SecretCodeResponse200Schema, 'description': 'Generating success'},
    500: {'model': SecretCodeResponseErrorSchema, 'description': 'Generating error'},
}


@router.get("/secretcode", status_code=status.HTTP_200_OK, response_model=SecretCodeResponse200Schema,
            description=description, responses=responses)
async def secret_code(response: Response):
    try:
        data_generate = await generate()
        data = SecretCodeResponse200Schema(
            code=data_generate['code'],
            state=data_generate['state']
        )
        return data
    except Exception as _ex:
        server_logger.error(f'Error generating secret code | {_ex}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'ok': False,
                                                                                        'error': 'Generating secret code error',
                                                                                        'msg': str(_ex)})


