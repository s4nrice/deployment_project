"""
Главный модуль FastAPI приложения для получения прогноза погоды.
"""
from fastapi import FastAPI, HTTPException, Request, status
from contextlib import asynccontextmanager
import redis.asyncio as redis
from prometheus_client import make_asgi_app
from dotenv import load_dotenv
import httpx

from app.config import settings
from app.weather_service import WeatherService
from app.rate_limiter import RateLimiter
from app.metrics import (
    REQUEST_COUNT,
    REQUEST_DURATION,
    ACTIVE_REQUESTS,
    REDIS_CONNECTION,
    RATE_LIMIT_HITS
)

# Загрузка переменных окружения
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация Redis
    app.state.redis = await redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        encoding="utf-8",
        decode_responses=True
    )
    
    # Проверка подключения к Redis
    try:
        await app.state.redis.ping()
        REDIS_CONNECTION.set(1)
    except Exception:
        REDIS_CONNECTION.set(0)
        raise
    
    # Инициализация сервисов
    app.state.weather_service = WeatherService(
        api_key=settings.OPENWEATHER_API_KEY,
        redis_client=app.state.redis
    )
    app.state.rate_limiter = RateLimiter(
        redis_client=app.state.redis,
        max_requests=settings.RATE_LIMIT_REQUESTS,
        window_seconds=settings.RATE_LIMIT_WINDOW
    )
    
    yield
    
    # Закрытие подключений
    await app.state.redis.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API для получения почасового прогноза погоды на текущий день",
    lifespan=lifespan
)

# Подключение Prometheus метрик
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware для сбора метрик."""
    ACTIVE_REQUESTS.inc()
    
    method = request.method
    endpoint = request.url.path
    
    with REQUEST_DURATION.labels(method=method, endpoint=endpoint).time():
        try:
            response = await call_next(request)
            status_code = response.status_code
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
            return response
        except Exception as e:
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
            raise
        finally:
            ACTIVE_REQUESTS.dec()


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Weather API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check(request: Request):
    """Проверка здоровья приложения."""
    try:
        # Проверка Redis
        await request.app.state.redis.ping()
        redis_status = "ok"
        REDIS_CONNECTION.set(1)
    except Exception:
        redis_status = "error"
        REDIS_CONNECTION.set(0)
    
    return {
        "status": "healthy" if redis_status == "ok" else "degraded",
        "redis": redis_status
    }


@app.get("/weather/{city}")
async def get_weather(city: str, request: Request):
    """
    Получить почасовой прогноз погоды на текущий день для указанного города.
    
    - **city**: Название города (например: Moscow, London, New York)
    
    Возвращает список почасовых прогнозов на текущий день.
    """
    # Проверка rate limit
    is_allowed = await request.app.state.rate_limiter.check_rate_limit()
    
    if not is_allowed:
        RATE_LIMIT_HITS.inc()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 60 requests per minute."
        )
    
    # Получение данных о погоде
    try:
        weather_data = await request.app.state.weather_service.get_weather(city)
        return weather_data
    except ValueError as e:
        # Ошибки конфигурации API ключа
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except httpx.HTTPStatusError as e:
        # HTTP ошибки от внешнего API
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching weather data: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

