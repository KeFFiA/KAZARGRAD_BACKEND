from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from BOT.Utils import dialogs
from DATABASE.database import db

async def create_vk_login():
    web_app = InlineKeyboardButton(text=dialogs.RU_ru_buttons['vk_id'], web_app=WebAppInfo(url='https://kazargrad.tw1.ru/api/vk-login/login'))
    back = InlineKeyboardButton(text=dialogs.RU_ru_buttons['back'], callback_data='admin_menu')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app], [back]])
    return keyboard


async def create_admin_menu():
    add = InlineKeyboardButton(text=dialogs.RU_ru_buttons['add'], callback_data='add')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[add]])
    return keyboard


async def create_add_choose():
    home = InlineKeyboardButton(text=dialogs.RU_ru_buttons['home'], callback_data='add_home')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[home]])
    return keyboard