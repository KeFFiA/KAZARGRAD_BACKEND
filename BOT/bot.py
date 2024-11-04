import asyncio
import json
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from BOT.Handlers.admin_handlers import admin_router
from BOT.Handlers.user_handlers import user_router
from BOT.Utils.dialogs import commands
from SERVER.Webhooks.telegram_webhook import redis_client
from LOGGING_SETTINGS.settings import bot_logger

load_dotenv()


async def process_update():
    bot_logger.info('Starting BOT...')
    bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode="HTML"))
    await bot.set_webhook(url=os.getenv("BASE_URL")+"/webhook/tg/", drop_pending_updates=True,
                          secret_token=os.getenv('BOT_SECRET'))
    await bot.set_my_commands(commands)
    dp = Dispatcher()
    dp.include_routers(user_router, admin_router)
    bot_logger.info('BOT successfully started')
    while True:
        try:
            update_json = redis_client.blpop('telegram_updates', timeout=0)[1]
            update_data = json.loads(update_json.decode('utf-8'))
            await dp.feed_raw_update(bot, update=update_data)
        except:
            await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(process_update())
