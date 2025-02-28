import asyncio
import os

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from LOGGING_SETTINGS.settings import server_logger
from SERVER.Utils.PKCE import router as pkce
from SERVER.Utils.SECRETCode import router as secrets
from SERVER.Routes.Telegram import router as tg_api
from SERVER.Routes.VK import router as vk_api
from SERVER.Routes.Booking import router as tilda_api
from SERVER.Routes.Yandex import router as yandex_api

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))

# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "https://kazargrad.tilda.ws"
# ]

app = FastAPI(redoc_url='/api/documentation',
              version='1.0.0',
              description='API documentation for **Kazargrad**',
              title='KAZARGRAD',
              )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="KAZARGRAD API",
        version="1.0.0",
        description="API documentation for **Kazargrad**",
        routes=api_router_v1.routes,
    )
    for path, methods in openapi_schema["paths"].items():
        for method, details in methods.items():
            if "responses" in details and "422" in details["responses"]:
                del details["responses"]["422"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router_v1 = APIRouter(prefix='/api/v1')
api_router_v1_utils = APIRouter(prefix='/utils')

api_router_v1.include_router(router=tg_api, include_in_schema=False)
api_router_v1.include_router(vk_api)
api_router_v1.include_router(tilda_api)
api_router_v1.include_router(yandex_api)

# Utils routers
api_router_v1_utils.include_router(pkce)
api_router_v1_utils.include_router(secrets)

api_router_v1.include_router(api_router_v1_utils, tags=["Utils"])
app.include_router(api_router_v1)


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
