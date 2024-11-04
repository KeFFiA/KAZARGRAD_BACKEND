from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from BOT.Utils import dialogs
from DATABASE.database import db

async def create_vk_login():
    web_app = InlineKeyboardButton(text=dialogs.RU_ru_buttons['vk_id'], web_app=WebAppInfo(url='https://kazargrad.tw1.ru/api/vk-login/login'))
    back = InlineKeyboardButton(text=dialogs.RU_ru_buttons['back'], callback_data='admin_menu')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app], [back]])
    return keyboard