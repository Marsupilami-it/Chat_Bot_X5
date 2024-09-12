from redis import Redis
from typing import Optional

# from models import ChatRequest
import logging
from api_service.settings import redis_config as conf

logger = logging.getLogger(__name__)


class CacheServer:
    def __init__(self):
        self.host = conf.redis_host
        self.port = conf.redis_port
        self.db = conf.redis_db
        self.client = Redis(host=self.host, port=self.port, db=self.db)

    def get(self, key: str) -> Optional[bytes]:
        """Возвращает значение по ключу, или None, если ключ не найден."""
        return self.client.get(key)

    def set(self, key: str, value: bytes, expire: Optional[int] = None):
        """Сохраняет значение по ключу, с опцией установки срока жизни (expire)."""
        self.client.set(key, value, ex=expire)

    def delete(self, key: str):
        """Удаляет ключ."""
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Проверяет существование ключа."""
        return self.client.exists(key)

    def flush_db(self):
        """Отчистка БД."""
        self.client.flushdb()

    def incr(self, key: str, amount: int = 1):
        """Увеличивает значение по ключу на amount."""
        self.client.incr(key, amount)

    def decr(self, key: str, amount: int = 1):
        """Уменьшает значение по ключу на amount."""
        self.client.decr(key, amount)

    def hset(self, key: str, field: str, value: bytes):
        """Устанавливает значение value для поля field в хэш-ключе key."""
        self.client.hset(key, field, value)

    def hget(self, key: str, field: str) -> Optional[bytes]:
        """Получает значение поля field из хэш-ключа key, или None, если поле не найдено."""
        return self.client.hget(key, field)

    def track_request(self):
        """Отслеживает количество запросов."""
        self.incr("request_count")

    # def save_request(self, request: ChatRequest, expire: Optional[int] = None):
    #     """Сохраняет запрос в Redis."""
    #     try:
    #         self.client.set(request.user_id, request.json(), ex=expire)
    #     except Exception as e:
    #         logger.error(f"Ошибка сохранения запроса в Redis: {e}")
    #
    # def get_request(self, user_id: str) -> Optional[ChatRequest]:
    #     """Получает запрос из Redis."""
    #     try:
    #         data = self.client.get(user_id)
    #         if data:
    #             return ChatRequest.parse_raw(data)
    #         else:
    #             return None
    #     except Exception as e:
    #         logger.error(f"Ошибка получения запроса из Redis: {e}")
    #         return None
