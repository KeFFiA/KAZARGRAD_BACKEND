import json
import os
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError



router = APIRouter(prefix='/tg', tags=['Telegram webhooks'])


@router.post("/")
async def webhook(request: Request):
    from DATABASE.redis_client import RedisClient
    from LOGGING_SETTINGS.settings import server_logger
    from dotenv import load_dotenv

    redis = RedisClient()

    load_dotenv()
    BOT_SECRET = os.getenv("BOT_SECRET")

    try:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token is None or secret_token != BOT_SECRET:
            server_logger.error('403 | Invalid or missing token: {}'.format(request.url))
            raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing token {}'.format(request.url)")

        data: Dict[str, Any] = await request.json()
        await redis.rpush('telegram_updates', json.dumps(data))
        return JSONResponse(status_code=200, content="ok")

    except ValidationError as _ex:
        server_logger.error('500 | Validation error: {}'.format(_ex))
        raise HTTPException(status_code=400, detail={"error": f"Validation error: {_ex}"})
    except Exception as _ex:
        server_logger.error('500 | Unknown error: {}'.format(_ex))
        raise HTTPException(status_code=500, detail={"error": f"Internal server error: {_ex}"})



