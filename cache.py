import redis

from settings import settings
from logger import logger

r = redis.Redis(host='redis', port=settings.redis.redis_port, password=settings.redis.redis_password)

try:
    response = r.ping()
    if response:
        pass
    else:
        logger.error("Не удалось подключиться к Redis.")
except redis.exceptions.RedisError as e:
    logger.error(f"Ошибка подключения к Redis: {e}")