import asyncio
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from LOGGING_SETTINGS.settings import server_logger
from SERVER.API.vk_api import router as vk_api
from SERVER.Utils.PKCE import router as pkce
from SERVER.Webhooks.telegram_webhook import router as tg_webhook
from SERVER.Webhooks.vk_webhook import router as vk_webhook

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://kazargrad.tw1.ru"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pkce)

app.include_router(tg_webhook)
app.include_router(vk_webhook)

app.include_router(vk_api)


@app.get("/", status_code=200)
async def root():
    return {"Hello": "World"}


async def start():
    server_logger.info('Starting SERVER...')
    try:
        import uvicorn
        config_path = os.path.join(base_dir, '..', 'LOGGING_SETTINGS', "config.json")
        uvicorn.run("SERVER.START:app", reload=True, log_level='debug', log_config=config_path)
    except Exception as _ex:
        server_logger.critical(f'SERVER start failed with error: {_ex}')


if __name__ == '__main__':
    asyncio.run(start())
