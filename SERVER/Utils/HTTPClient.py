from aiohttp import ClientSession

class HTTPClient:
    def __init__(self, base_url: str):
        self._session = ClientSession(
            base_url=base_url
        )
        self._closed = False

    async def close(self):
        if not self._closed:
            await self._session.close()
            self._closed = True

