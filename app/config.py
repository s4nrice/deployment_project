"""
Конфигурация приложения.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    
    # OpenWeatherMap API
    OPENWEATHER_API_KEY: str
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Application
    APP_NAME: str = "Weather API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60  # секунды
    
    # Cache
    CACHE_TTL: int = 3600  # секунды
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

