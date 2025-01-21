import os
from redis.asyncio import Redis
from dotenv import load_dotenv

load_dotenv()

class RedisClient:
    def __init__(self, host: str = os.getenv("REDIS_HOST"), port: int = int(os.getenv("REDIS_PORT")), db: int = 0):
        self.client = Redis(host=host, port=port, db=db)

    async def close(self):
        await self.client.close()

    async def get(self, key: str):
        return await self.client.get(key)

    async def set(self, key: str, value: str):
        return await self.client.set(key, value)

    async def delete(self, key: str):
        return await self.client.delete(key)

    async def rpush(self, key: str, value: str):
        return await self.client.rpush(key, value)

    async def blpop(self, key: list[str] | str, timeout: int | float | None = 0):
        return await self.client.blpop(key, timeout)
