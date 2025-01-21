import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from BOT.Utils import dialogs
from DATABASE.database import db


class CheckInAdminListMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.admin_users = []

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        user_id = data["event_from_user"].id
        users = db.query(query="SELECT user_id FROM white_list WHERE admin=true", fetch='fetchall')
        self.admin_users = [item for tup in users for item in tup]
        if user_id in self.admin_users:
            return await handler(event, data)
        else:
            try:
                return await event.message.answer(
                    dialogs.RU_ru['not_admin'].format(user_id),
                    parse_mode='HTML', show_alert=False
                )
            except:
                return await event.answer(
                    dialogs.RU_ru['not_admin'].format(user_id),
                    parse_mode='HTML', show_alert=True
                )


class CheckAccessTokenMiddleware(BaseMiddleware):
    def __init__(self):
        from DATABASE.redis_client import redis_client as redis
        super().__init__()
        self.access_token_vk, self.access_token_avito = None, None
        self.redis = redis
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        self.user_id = data["event_from_user"].id
        self.access_token_vk = self.redis.get('vk_token:last_update')
        self.access_token_avito = self.redis.get('avito_token:last_update')
        # if self.access_token_vk or self.access_token_avito is None:
        if self.access_token_vk:
            self.result = 'Error'
        else:
            self.access_token_vk = int(self.access_token_vk)
            self.current_time = int(time.time())
            self.time_difference_vk = (self.current_time - self.access_token_vk) // 3600
            if self.time_difference_vk < 1:
                return await handler(event, data)
            else:
                self.result = 'Error'

