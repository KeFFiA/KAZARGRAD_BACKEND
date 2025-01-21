import asyncio
import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from BOT.Utils.BookingUpdates import check_booking_requests
from BOT.bot import process_update


async def start():
    await asyncio.gather(process_update(), check_booking_requests())


if __name__ == '__main__':
    asyncio.run(start())
    # asyncio.run(process_update())
    # asyncio.get_event_loop().run_until_complete(check_booking_requests())

