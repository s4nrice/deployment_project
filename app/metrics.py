"""
Модуль для настройки Prometheus метрик.
"""
from prometheus_client import Counter, Histogram, Gauge

# Метрики кэширования
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Метрики HTTP запросов
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Active HTTP requests'
)

# Метрики Redis
REDIS_CONNECTION = Gauge(
    'redis_connection_status',
    'Redis connection status (1=connected, 0=disconnected)'
)

# Метрики rate limiting
RATE_LIMIT_HITS = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits'
)

def setup_metrics():
    """Настройка метрик (заглушка для будущего расширения)."""
    pass

