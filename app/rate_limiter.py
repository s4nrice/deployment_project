"""
Глобальный rate limiter на основе Redis.
"""
import redis.asyncio as redis
from datetime import datetime, timezone
from app.config import settings


class RateLimiter:
    """Глобальный rate limiter для всего приложения."""
    
    RATE_LIMIT_KEY = "rate_limit:global"
    
    def __init__(self, redis_client: redis.Redis, max_requests: int, window_seconds: int):
        """
        Инициализация rate limiter.
        
        Args:
            redis_client: Клиент Redis
            max_requests: Максимальное количество запросов
            window_seconds: Окно времени в секундах
        """
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def check_rate_limit(self) -> bool:
        """
        Проверка rate limit.
        
        Returns:
            True если запрос разрешен, False если превышен лимит
        """
        current_time = datetime.now(timezone.utc).timestamp()
        window_start = current_time - self.window_seconds
        
        # Используем Redis sorted set для хранения временных меток запросов
        # Удаляем старые записи (старше окна)
        await self.redis.zremrangebyscore(
            self.RATE_LIMIT_KEY,
            0,
            window_start
        )
        
        # Подсчитываем количество запросов в текущем окне
        current_count = await self.redis.zcard(self.RATE_LIMIT_KEY)
        
        if current_count >= self.max_requests:
            return False
        
        # Добавляем текущий запрос
        await self.redis.zadd(
            self.RATE_LIMIT_KEY,
            {str(current_time): current_time}
        )
        
        # Устанавливаем TTL для ключа (на случай если все записи удалятся)
        await self.redis.expire(self.RATE_LIMIT_KEY, self.window_seconds)
        
        return True

