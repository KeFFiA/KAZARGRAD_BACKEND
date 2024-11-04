import os

import redis
from dotenv import load_dotenv

# from LOGGING_SETTINGS.settings import database_logger

load_dotenv()

class RedisClient:
    def __init__(self, host: str = os.getenv("REDIS_HOST"), port: str|int = os.getenv("REDIS_PORT"), db = 0):
        try:
            if port is str:
                port = int(port)
            self.client = redis.Redis(host=host, port=port, db=db)
            # database_logger.debug("Redis client connected")
        except Exception as _ex:
            ...
            # database_logger.critical("Redis client connection failed: {}".format(_ex))

    def close(self):
        self.client.close()

    def get(self, key: str):
        return self.client.get(key)

    def set(self, key: str, value: str):
        return self.client.set(key, value)

    def delete(self, key: str):
        return self.client.delete(key)

redis_client = RedisClient()

