import json
import os
from typing import Dict, Any

import redis
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from LOGGING_SETTINGS.settings import server_logger

load_dotenv()
router = APIRouter(prefix='/webhook/tg', tags=['tg_webhook'])
BOT_SECRET = os.getenv("BOT_SECRET")
redis_client = redis.from_url(os.getenv("REDIS_URL"))


@router.post("/")
async def webhook(request: Request):
    try:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token is None or secret_token != BOT_SECRET:
            server_logger.error('403 | Invalid or missing token: {}'.format(request.url))
            raise HTTPException(status_code=403, detail="Forbidden: Invalid or missing token")

        data: Dict[str, Any] = await request.json()
        redis_client.rpush('telegram_updates', json.dumps(data))
        return JSONResponse(status_code=200, content="ok")

    except ValidationError as _ex:
        server_logger.error('500 | Validation error: {}'.format(_ex))
        return JSONResponse(status_code=400, content={"error": f"Validation error: {_ex}"})
    except Exception as _ex:
        server_logger.error('500 | Unknown error: {}'.format(_ex))
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {_ex}"})



