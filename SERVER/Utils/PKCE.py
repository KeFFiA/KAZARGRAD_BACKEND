import base64
import hashlib
import json
import os
import random
import string

from dotenv import load_dotenv
from fastapi import APIRouter, Response
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import JSONResponse

from DATABASE.redis_client import RedisClient
from LOGGING_SETTINGS.settings import server_logger

load_dotenv()


async def generate(verifier=None):
    redis = RedisClient()
    if verifier is None:
        length = random.randint(43, 128)
        chars = string.ascii_letters + string.digits + '-._~'
        verifier = ''.join(random.choice(chars) for _ in range(length))

    code_verifier_bytes = verifier.encode('utf-8')
    code_challenge = hashlib.sha256(code_verifier_bytes).digest()
    challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')
    state = os.urandom(16).hex()

    data = {
        'verifier': verifier,
        'challenge': challenge,
        'state': state
    }

    await redis.set(f'pkce:{state}', json.dumps(data))
    await redis.close()
    return verifier, challenge, state


router = APIRouter()


class PKCERequestSchema(BaseModel):
    app_name: str = Field(default=..., title='', description='The name of the application for which the generation',
                           examples=['YANDEX', 'VK'])


class PKCEResponse200Schema(BaseModel):
    ok: bool = Field(default=True, title="", description='Operation status')
    verifier: str = Field(default=..., title='', description='Verifier code',
                          examples=['xVmRHy~kqnvE.2_DM.f3omgAuIiv54pdWfL~EKSdmDMs4yLkDd3'], min_length=43,
                          max_length=128)
    challenge: str = Field(default=..., title='', description='Challenge code',
                           examples=['oFk-zwxsPYrjYn53pLYH_6mTZzoDa_GhvLK8Fu0HeS8'], min_length=43, max_length=43)
    state: str = Field(default=..., title='', description='Verification state string',
                       examples=['ebf2b96ac0d5918206aa95e5747dcaee'], min_length=32, max_length=32)
    app_id: str = Field(default=..., title='', description='The name of the application for which the generation',
                         examples=['61795935', '4b12v4hc1y2y7fwee787ds'])


class PKCEResponseErrorSchema(BaseModel):
    ok: bool = Field(title="", default=False, description="Operation status")
    error: str = Field(title='', description="Description of error")
    msg: str = Field(title='', description="Message of error")


description = """
Method for generating secret code
"""

responses = {
    200: {'model': PKCEResponse200Schema, 'description': 'Generating success'},
    500: {'model': PKCEResponseErrorSchema, 'description': 'Generating error'},
}


@router.get("/pkce", status_code=status.HTTP_200_OK, response_model=PKCEResponse200Schema,
            description=description, responses=responses)
async def pkce(data: PKCERequestSchema, response: Response):
    try:
        if data.app_name == 'VK':
            app = os.getenv('VK_APP_ID')
        elif data.app_name == 'YANDEX':
            app = os.getenv('YANDEX_APP_ID')
        else:
            app = os.getenv('APP_ID')
        verifier, challenge, state = await generate()
        data = {
            'verifier': verifier,
            'challenge': challenge,
            'state': state,
            'app_id': app,
        }
        return data
    except Exception as _ex:
        server_logger.error(f'Error generating PKCE | {_ex}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'ok': False,
                                                                                        'error': f'Error generating PKCE',
                                                                                        'msg': str(data.state)})
