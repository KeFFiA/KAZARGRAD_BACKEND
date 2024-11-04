import redis
from dotenv import load_dotenv
import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
import vk_api

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/api/vk", tags=["vk_api"])

@router.get('/login')
async def vk_login(code: str, device_id: str, state: str):
    ...


# @router.get('/logout')

