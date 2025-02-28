import asyncio
import datetime
import json
import pytz

from BOT.bot import bot
from DATABASE.redis_client import RedisClient
from LOGGING_SETTINGS.settings import bot_logger



async def check_booking_requests():
    redis = RedisClient()
    while True:
        try:
            booking_json = await redis.blpop('booking_requests')
            booking_data = json.loads(booking_json[1].decode('utf-8'))
            # TODO: ADD LOGGER
            await send_booking_requests(data=booking_data)
        except:
            await asyncio.sleep(0.1)


async def send_booking_requests(data: dict):
    time_now_ = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
    total_guests = data['adults'] + data['child1'] + data['child2']
    if data['type'] == 'house':
        booking_type = 'Домик'
    else:
        booking_type = 'Банкетный домик'
    child1_text = ''
    child2_text = ''

    if data['child1'] > 0:
        child1_text += f'<b>Детей до 6 лет --></b> {data["child1"]}'
    if data['child2'] > 0:
        child2_text += f'<b>Детей старше 6 лет --></b> {data["child2"]}'

    if data['request_from'] == 'Web-site':
        request_from = 'Сайт'

    message = f"""‼<b>ЗАЯВКА НА БРОНЬ</b>‼

<b>Тип --></b> {booking_type} 

<b>ФИО --></b> {data['name']}
<b>Номер телефона --></b> {data['phone']}
<b>Почта --></b> {data['email']}

<b>Дата въезда --></b> {data['from']}
<b>Дата выезда --></b> {data['to']}

<b>Гостей --></b> {total_guests}, из них:
    <b>Взрослых --> </b> {data['adults']}
    {child1_text}
    {child2_text}
    
<b>Время поступления заявки --></b> {time_now_.strftime("%Y-%m-%d | %H:%M")}

<b>Откуда поступила заявка --></b> {request_from}
"""
    await bot.send_message(chat_id=409445811, text=message)