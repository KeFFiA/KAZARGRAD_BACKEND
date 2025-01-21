import asyncio
import json
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from BOT.Handlers.admin_handlers import admin_router
from BOT.Handlers.user_handlers import user_router
from BOT.Utils.dialogs import commands
from LOGGING_SETTINGS.settings import bot_logger

load_dotenv()


dp = Dispatcher()
dp.include_routers(user_router, admin_router)
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))


async def process_update():
    from DATABASE.redis_client import RedisClient
    redis = RedisClient()
    bot_logger.info('Starting BOT...')
    await bot.set_webhook(url=os.getenv("BASE_URL") + "/api/v1/tg/", drop_pending_updates=True,
                          secret_token=os.getenv('BOT_SECRET'))
    await bot.set_my_commands(commands)
    bot_logger.info('BOT successfully started')
    while True:
        try:
            update_json = await redis.blpop(key='telegram_updates')
            update_data = json.loads(update_json[1].decode('utf-8'))
            # TODO: ADD LOGGER
            await dp.feed_raw_update(bot, update=update_data)
        except:
            await asyncio.sleep(0.1)
