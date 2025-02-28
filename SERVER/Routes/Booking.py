import json

from fastapi import APIRouter, status, Response, Query
from pydantic import BaseModel, Field
from datetime import date

from starlette.responses import JSONResponse

router = APIRouter(prefix="/booking", tags=["Booking"])

class BookingRequestSchema(BaseModel):
    code: int = Field(default=..., title="", description="Verification code", examples=['123456'])
    state: str = Field(default=..., title="", description="Verification state string", examples=['ebf2b96ac0d5918206aa95e5747dcaee'], min_length=32, max_length=32)
    request_from: str = Field(default=..., title="", description="Where is the request sent from", examples=['Web-site'], min_length=1, max_length=16)
    date_from: date = Field(default=..., title="", description="Booking start date", examples=['2025-01-25'])
    date_to: date = Field(default=..., title="", description="Booking end date", examples=['2025-01-27'])
    adults: int = Field(default=..., title="", description="Adults count", examples=['2'])
    child1: int | None = Field(default=None, title="", description="Child(1-6 y.o.) count", examples=['2'])
    child2: int | None = Field(default=None, title="", description="Child(7-17 y.o.) count", examples=['1'])
    type: str = Field(default=..., title="", description="Booking type", examples=['house'])


class BookingResponse201Schema(BaseModel):
    ok: bool = Field(title="", default=True, description='Operation status')
    id: int = Field(default=..., title="", description="Booking ID", examples=['123456'])


class BookingResponseErrorSchema(BaseModel):
    ok: bool = Field(title="", default=False, description='Operation status')
    error: str = Field(title='', description="Description of error")
    msg: str = Field(title='', description="Message of error")


description = """
Creating booking request
"""

responses = {
    201: {"model": BookingResponse201Schema, "description": "Booking request created"},
    400: {"model": BookingResponseErrorSchema, "description": "PKCE data not found"},
    401: {"model": BookingResponseErrorSchema, "description": "Invalid secret code"},
    500: {"model": BookingResponseErrorSchema, "description": "Booking request failed"},
}

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=BookingResponse201Schema,
             description=description, responses=responses)
async def create(data: BookingRequestSchema, response: Response):
    from DATABASE.redis_client import RedisClient
    from LOGGING_SETTINGS.settings import server_logger
    redis = RedisClient()
    try:
        server_logger.info('Received booking webhook')
        code_json = await redis.get(f'secret_code:{data.state}')

        if not code_json:
            server_logger.warn(f'Invalid state or PKCE data not found | {data.state}')
            response.status_code = status.HTTP_400_BAD_REQUEST
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'ok': False,
                                                                                  'error': f'Invalid state or PKCE data not found',
                                                                                  'msg': f'Invalid state or PKCE data not found | {data.state}'})

        code_data = json.loads(code_json.decode('utf-8'))

        if data.code != int(code_data['code']):
            server_logger.warn(f'Invalid secret code | {data.code}')
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={'ok': False,
                                                                                   'error': 'Invalid secret code',
                                                                                   'msg': f'Invalid secret code | {data.code}'})

        booking_data = {
            'request_from': data.request_from,
            'from': data.date_from.strftime('%Y-%m-%d'),
            'to': data.date_to.strftime('%Y-%m-%d'),
            'adults': data.adults,
            'child1': data.child1,
            'child2': data.child2,
            'type': data.type,
            'id': 1312312
        }
        await redis.rpush('booking_requests', json.dumps(booking_data))
        server_logger.info(f'Booking data received: {booking_data}')
        return BookingResponse201Schema(id=booking_data['id'], ok=True)
    except Exception as _ex:
        server_logger.error(f'Booking request failed: {_ex}')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'ok': False,
                                                                                        'error': 'Booking request failed',
                                                                                        'msg': f'{_ex}'})
    finally:
        await redis.close()



class BookingGetInfoSchema(BaseModel):
    date_from: str = Field(default=..., title="", description="Booking start date", examples=['2025-01-25'])
    date_to: str = Field(default=..., title="", description="Booking end date", examples=['2025-01-27'])
    adults: int = Field(default=..., title="", description="Adults count", examples=['2'])
    child1: int | None = Field(default=None, title="", description="Child(1-6 y.o.) count", examples=['2'])
    child2: int | None = Field(default=None, title="", description="Child(7-17 y.o.) count", examples=['1'])
    type: str = Field(default=..., title="", description="Booking type", examples=['house'])


@router.get('/get', response_model=BookingGetInfoSchema, responses={200: {'model': BookingGetInfoSchema}})
async def get_info(response: Response):
    data = BookingGetInfoSchema(date_from='2025-01-21', date_to='2025-01-29', adults=2, child1=2, child2=2, type='house')
    return data




