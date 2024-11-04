from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from BOT.Utils import dialogs
from DATABASE.database import db


user_router = Router()

# COMMANDS/MESSAGES

@user_router.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext):
    await message.answer(dialogs.RU_ru_text['/start'].format(message.from_user.first_name))
    db.query(
        query="INSERT INTO users (user_id, username, user_name, user_surname) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
        values=(
            message.from_user.id, message.from_user.username, message.from_user.first_name,
            message.from_user.last_name),
        log_level=10,
        msg=f'User {message.from_user.id} already exist')

    await state.clear()


