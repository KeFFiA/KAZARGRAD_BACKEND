from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, WebAppData
from aiohttp import ClientSession

from BOT.Keyboards.Inline_keyboards import create_vk_login
from BOT.START import bot
from BOT.Utils import dialogs
from BOT.Utils.States import AddHome
from DATABASE.database import db
from LOGGING_SETTINGS.settings import market_logger

market_router = Router()

# MESSAGES | COMMANDS


@market_router.callback_query(F.data.startswith('add'))
async def add_query(call: CallbackQuery, state: FSMContext):
    if call.data == 'add':
        await call.message.edit_text(text=dialogs.RU_ru_text['add']['text'])
    if call.data == 'add_home':
        await call.message.edit_text(text=dialogs.RU_ru_text['add']['main_photo']+dialogs.RU_ru_text['add']['home']['text'])
        await state.set_state(AddHome.image)

# STATES

@market_router.message(AddHome.image)
async def add_home_image(message: Message):
    if message.photo:
        _type = 'photo'
        file_id = message.photo[-1].file_id
        file_name = f"{message.photo[-1].file_id}.jpg"
    elif message.video:
        _type = 'video'
        file_id = message.video.file_id
        file_name = f"{message.video.file_id}.mp4"

    file_path = await bot.download_file(file_id, file_name)
    async with ClientSession() as session:
        async with session.post(url='/home/add/file', params={'type': _type, 'file_path': file_path}) as response:
            if response.status != 200:
                market_logger.error(f'Send file error: {response.status}')
                return


