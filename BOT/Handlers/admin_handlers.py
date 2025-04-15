import os

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, WebAppData
from aiohttp import ClientSession

from BOT.Keyboards.Inline_keyboards import create_vk_login, create_admin_menu
from BOT.Utils import dialogs
from DATABASE.database import db

admin_router = Router()

# MESSAGES | COMMANDS


@admin_router.message(Command('admin'))
async def admin_cmd(message: Message):
    await message.answer(text=dialogs.RU_ru_text['/admin'], reply_markup=await create_admin_menu())



@admin_router.message(Command('login'))
async def admin_login(message: Message):
    async with ClientSession() as session:
        async with session.get('http://127.0.0.1:8000/api/v1/utils/pkce', json={'app_name': 'YANDEX'}) as response:
            data = await response.json()
    yandex_url = ('https://oauth.yandex.ru/authorize?response_type=code&redirect_uri={redirect_url}&client_id={client_id}'
                  '&login_hint=Kazargrad-rzn@yandex.ru&force_confirm=true&state={state}&code_challenge={code_challenge}'
                  '&code_challenge_method=S256&code_verifier={code_verifier}').format(
        redirect_url=os.getenv('BASE_URL') + '/api/v1/yandex/auth',
        client_id=data['app_id'],
        code_challenge=data['challenge'],
        code_verifier=data['verifier'],
        state=data['state'],
    )
    # vk_url = f'{os.getenv("TEST_URL_2")}/api/vk-login/login'
    async with ClientSession() as session:
        async with session.get('http://127.0.0.1:8000/api/v1/utils/pkce', json={'app_name': 'VK'}) as response:
            data = await response.json()

    vk_url = ('https://id.vk.com/authorize?response_type=code&client_id={client_id}'
              '&redirect_uri={redirect_url}&state={state}&code_challenge={code_challenge}'
              '&code_challenge_method=S256&scope={scope}&prompt={prompt}').format(
        redirect_url=os.getenv('BASE_URL') + '/api/v1/vk/auth',
        client_id=data['app_id'],
        state=data['state'],
        code_challenge=data['challenge'],
        scope='phone community market',
        prompt=''
    )
    await message.answer(text=f"VK: <a href='{vk_url}'>Войти в ВК</a>\n\nYANDEX: <a href='{yandex_url}'>Войти в Яндекс</a>")




