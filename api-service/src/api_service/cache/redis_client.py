from os import getenv
from typing import Optional
from redis import Redis
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.host = getenv("REDIS_HOST")
        self.port = int(getenv("REDIS_PORT"))
        self.db = int(getenv("REDIS_DB", 0))
        self.client = Redis(host=self.host, port=self.port, db=self.db)

    def get(self, key: str) -> Optional[bytes]:
        """Возвращает значение по ключу, или None, если ключ не найден."""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Ошибка получения значения по ключу: {e}")
            return None

    def set(self, key: str, value: bytes, expire: Optional[int] = None):
        """Сохраняет значение по ключу, с опцией установки срока жизни (expire)."""
        try:
            self.client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Ошибка сохранения значения по ключу: {e}")

    def delete(self, key: str):
        """Удаляет ключ."""
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Ошибка удаления ключа: {e}")

    def exists(self, key: str) -> bool:
        """Проверяет существование ключа."""
        try:
            return self.client.exists(key)
        except Exception as e:
            logger.error(f"Ошибка проверки существования ключа: {e}")
            return False

    def flush_db(self):
        """Отчистка БД."""
        try:
            self.client.flushdb()
        except Exception as e:
            logger.error(f"Ошибка очистки БД: {e}")

    def incr(self, key: str, amount: int = 1) -> int:
        """Увеличивает значение по ключу на amount."""
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Ошибка увеличения значения по ключу: {e}")
            return 0

    def decr(self, key: str, amount: int = 1) -> int:
        """Уменьшает значение по ключу на amount."""
        try:
            return self.client.decr(key, amount)
        except Exception as e:
            logger.error(f"Ошибка уменьшения значения по ключу: {e}")
            return 0

    def hset(self, key: str, field: str, value: bytes):
        """Устанавливает значение value для поля field в хэш-ключе key."""
        try:
            self.client.hset(key, field, value)
        except Exception as e:
            logger.error(f"Ошибка установки значения для поля в хэш-ключе: {e}")

    def hget(self, key: str, field: str) -> Optional[bytes]:
        """Получает значение поля field из хэш-ключа key, или None, если поле не найдено."""
        try:
            return self.client.hget(key, field)
        except Exception as e:
            logger.error(f"Ошибка получения значения поля из хэш-ключа: {e}")
            return None

    def track_request(self):
        """Отслеживает количество запросов."""
        self.incr("request_count")
