"""
Сервис для получения данных о погоде из OpenWeatherMap API.
"""
import httpx
import redis.asyncio as redis
from datetime import datetime, timezone
from typing import List, Dict, Any
import json

from app.config import settings
from app.metrics import CACHE_HITS, CACHE_MISSES


class WeatherService:
    """Сервис для работы с погодными данными."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str, redis_client: redis.Redis):
        """
        Инициализация сервиса.
        
        Args:
            api_key: API ключ OpenWeatherMap
            redis_client: Клиент Redis для кэширования
        """
        self.api_key = api_key
        self.redis = redis_client
    
    def _get_cache_key(self, city: str, date: str) -> str:
        """Генерация ключа кэша."""
        return f"weather:{city.lower()}:{date}"
    
    async def _get_from_cache(self, city: str, date: str) -> List[Dict[str, Any]] | None:
        """Получение данных из кэша."""
        cache_key = self._get_cache_key(city, date)
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            CACHE_HITS.labels(cache_type="weather").inc()
            return json.loads(cached_data)
        
        CACHE_MISSES.labels(cache_type="weather").inc()
        return None
    
    async def _save_to_cache(self, city: str, date: str, data: List[Dict[str, Any]]):
        """Сохранение данных в кэш."""
        cache_key = self._get_cache_key(city, date)
        await self.redis.setex(
            cache_key,
            settings.CACHE_TTL,
            json.dumps(data)
        )
    
    async def _fetch_from_api(self, city: str) -> Dict[str, Any]:
        """Получение данных из OpenWeatherMap API."""
        if not self.api_key or self.api_key == "your_api_key_here":
            raise ValueError(
                "OpenWeatherMap API key is not configured. "
                "Please set OPENWEATHER_API_KEY in your .env file. "
                "Get your API key at: https://openweathermap.org/api"
            )
        
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "ru"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 401:
                raise ValueError(
                    "Invalid OpenWeatherMap API key. "
                    "Please check your OPENWEATHER_API_KEY in .env file. "
                    "Get your API key at: https://openweathermap.org/api"
                )
            response.raise_for_status()
            return response.json()
    
    def _filter_today_forecast(self, forecast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Фильтрация прогноза на текущий день.
        
        Args:
            forecast_data: Данные прогноза от API
            
        Returns:
            Список почасовых прогнозов на текущий день
        """
        now = datetime.now(timezone.utc)
        today = now.date()
        hourly_forecasts = []
        
        # OpenWeatherMap возвращает прогноз с интервалом 3 часа
        # Берем все прогнозы на текущий день, включая те, что еще не наступили
        for item in forecast_data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
            
            # Включаем прогнозы на сегодня, которые еще не прошли
            # или все прогнозы на сегодня, если день только начался
            if dt.date() == today and dt >= now.replace(hour=0, minute=0, second=0, microsecond=0):
                hourly_forecasts.append({
                    "datetime": dt.isoformat(),
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "description": item["weather"][0]["description"],
                    "wind_speed": item.get("wind", {}).get("speed", 0),
                    "clouds": item.get("clouds", {}).get("all", 0)
                })
        
        # Если для текущего дня нет данных (например, день уже закончился),
        # возвращаем ближайшие прогнозы на сегодня или завтра
        if not hourly_forecasts:
            # Берем первые несколько прогнозов из списка
            for item in forecast_data.get("list", [])[:8]:  # Берем первые 8 прогнозов (24 часа)
                dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
                hourly_forecasts.append({
                    "datetime": dt.isoformat(),
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "description": item["weather"][0]["description"],
                    "wind_speed": item.get("wind", {}).get("speed", 0),
                    "clouds": item.get("clouds", {}).get("all", 0)
                })
        
        return hourly_forecasts
    
    async def get_weather(self, city: str) -> Dict[str, Any]:
        """
        Получить почасовой прогноз погоды на текущий день.
        
        Args:
            city: Название города
            
        Returns:
            Словарь с данными о погоде
        """
        today = datetime.now(timezone.utc).date().isoformat()
        
        # Попытка получить из кэша
        cached_data = await self._get_from_cache(city, today)
        if cached_data:
            return {
                "city": city,
                "date": today,
                "forecast": cached_data,
                "cached": True
            }
        
        # Получение из API
        api_data = await self._fetch_from_api(city)
        forecast = self._filter_today_forecast(api_data)
        
        # Сохранение в кэш
        if forecast:
            await self._save_to_cache(city, today, forecast)
        
        return {
            "city": api_data["city"]["name"],
            "country": api_data["city"].get("country", ""),
            "date": today,
            "forecast": forecast,
            "cached": False
        }

