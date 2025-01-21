from aiohttp import ClientSession
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse


router = APIRouter(prefix='/home', tags=['Houses methods'])


@router.get('/add/file')
async def add_home_photo_webhook(request: Request):
    from LOGGING_SETTINGS.settings import server_logger
    server_logger.info('Received request to add home photo')

    async def upload_yandex(file_path, file_name):
        yandex_url = ('https://cloud-api.yandex.net/v1/disk/resources/upload?path={file_name}&overwrite=true'
                      .format(file_name=file_name))

        headers = {
            'Authorization': f'OAuth {YANDEX_DISK_TOKEN}'
        }

        async with ClientSession() as session:
            async with session.get(yandex_url, headers=headers) as response:
                if response.status != 200:
                    server_logger.error(f'Error while uploading {file_name} to yandex: {response.status}')
                result = await response.json()
        if response.status_code == 200:
            upload_url = response.json().get('href')

            # Загружаем файл
            with open(file_path, 'rb') as file:
                upload_response = requests.put(upload_url, files={'file': file})
                return upload_response.status_code == 201
        return False

    try:
        file_type = request.query_params.get('type')
        file_path = request.query_params.get('file_path')
        file_name = request.query_params.get('file_name')







