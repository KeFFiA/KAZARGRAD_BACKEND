from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from BOT.Keyboards.Inline_keyboards import create_vk_login
from BOT.Utils import dialogs
from DATABASE.database import db

admin_router = Router()

@admin_router.message(Command('login'))
async def login_cmd(message: Message):
    await message.answer(text=dialogs.RU_ru_text['/login'].format(message.from_user.first_name), reply_markup=await create_vk_login())

