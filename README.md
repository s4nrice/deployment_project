# Weather API - Учебный Backend Проект

Backend-приложение на FastAPI для получения почасового прогноза погоды на текущий день с использованием OpenWeatherMap API.

## 🚀 Возможности

- **API эндпоинт** `/weather/{city}` - получение почасового прогноза погоды
- **Кэширование** в Redis на 1 час
- **Глобальный rate limiting** - 60 запросов в минуту
- **Мониторинг** - Prometheus + Grafana
- **Документация API** - Swagger UI
- **CI/CD** - GitHub Actions

## 📋 Технологический стек

- **Backend**: FastAPI, Python 3.11
- **Кэш и Rate Limiting**: Redis
- **Мониторинг**: Prometheus, Grafana
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 🛠 Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- API ключ от OpenWeatherMap (получить можно на [openweathermap.org](https://openweathermap.org/api))

### Быстрый старт

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd deployment_project
```

2. **Создайте файл `.env`:**
```bash
cp env.example .env
```

3. **Отредактируйте `.env` и укажите ваш API ключ:**
```env
OPENWEATHER_API_KEY=your_api_key_here
```

4. **Запустите приложение:**
```bash
docker-compose up -d
```

5. **Проверьте статус сервисов:**
```bash
docker-compose ps
```

## 📡 API Эндпоинты

### Получить прогноз погоды

**GET** `/weather/{city}`

**Параметры:**
- `city` (path) - название города (например: Moscow, London, New York)

**Пример запроса:**
```bash
curl http://localhost:8888/weather/Moscow
```

**Пример ответа:**
```json
{
  "city": "Moscow",
  "country": "RU",
  "date": "2024-01-15",
  "forecast": [
    {
      "datetime": "2024-01-15T12:00:00+00:00",
      "temperature": 5.2,
      "feels_like": 3.1,
      "humidity": 65,
      "pressure": 1013,
      "description": "ясно",
      "wind_speed": 3.5,
      "clouds": 10
    }
  ],
  "cached": false
}
```

### Health Check

**GET** `/health`

Проверка состояния приложения и подключения к Redis.

### Документация API

**GET** `/docs`

Swagger UI документация доступна по адресу: http://localhost:8888/docs

## 🔧 Конфигурация

Все настройки находятся в файле `.env`:

```env
# OpenWeatherMap API
OPENWEATHER_API_KEY=your_api_key_here

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Rate Limiting
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60

# Cache
CACHE_TTL=3600
```

## 📊 Мониторинг

### Prometheus

Prometheus доступен по адресу: http://localhost:9090

Метрики приложения доступны по адресу: http://localhost:8888/metrics

### Grafana

Grafana доступна по адресу: http://localhost:3000

**Учетные данные по умолчанию:**
- Username: `admin`
- Password: `admin`

**Дашборды:**
- FastAPI Observability - основные метрики приложения

## 🏗 Архитектура проекта

```
deployment_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # Главный модуль FastAPI
│   ├── config.py            # Конфигурация
│   ├── weather_service.py   # Сервис для работы с погодой
│   ├── rate_limiter.py      # Rate limiting
│   └── metrics.py           # Prometheus метрики
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml   # Конфигурация Prometheus
│   └── grafana/
│       ├── provisioning/    # Автоматическая настройка Grafana
│       └── dashboards/      # Дашборды Grafana
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # CI/CD конфигурация
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🔒 Rate Limiting

Приложение использует глобальный rate limit:
- **Лимит**: 60 запросов в минуту
- **Реализация**: Redis sorted set
- **Ответ при превышении**: HTTP 429 Too Many Requests

## 💾 Кэширование

- **Хранилище**: Redis
- **Формат ключа**: `weather:{city}:{YYYY-MM-DD}`
- **TTL**: 3600 секунд (1 час)

## 🚀 Запуск приложения

### Локальный запуск (без Docker)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск Redis (через Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Запуск приложения
uvicorn app.main:app --reload
```

### Запуск через Docker

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f app

# Остановка
docker-compose down
```

## 📈 Метрики Prometheus

Приложение экспортирует следующие метрики:

- `http_requests_total` - общее количество HTTP запросов
- `http_request_duration_seconds` - длительность запросов
- `http_active_requests` - активные запросы
- `cache_hits_total` - попадания в кэш
- `cache_misses_total` - промахи кэша
- `rate_limit_hits_total` - срабатывания rate limit
- `redis_connection_status` - статус подключения к Redis

## 🚢 CI/CD

CI/CD настроен через GitHub Actions и включает:

1. **Линтинг** - проверка кода с помощью flake8 и black
2. **Сборка Docker образа** - при push в main ветку
3. **Публикация образа** - в Docker Hub (при наличии секретов)

Для настройки CI/CD необходимо добавить секреты в GitHub:
- `DOCKER_USERNAME` - имя пользователя Docker Hub
- `DOCKER_PASSWORD` - пароль Docker Hub

## 📝 Разработка

### Структура кода

- `app/main.py` - точка входа, FastAPI приложение
- `app/weather_service.py` - бизнес-логика работы с погодой
- `app/rate_limiter.py` - логика rate limiting
- `app/config.py` - управление конфигурацией

### Добавление новых функций

1. Создайте новый модуль в `app/`
2. Импортируйте и используйте в `app/main.py`
3. Обновите документацию

## 🐛 Устранение неполадок

### Приложение не запускается

1. Проверьте, что Redis запущен: `docker-compose ps`
2. Проверьте логи: `docker-compose logs app`
3. Убедитесь, что API ключ указан в `.env`

### Rate limit срабатывает слишком часто

Проверьте настройки в `.env`:
- `RATE_LIMIT_REQUESTS` - количество запросов
- `RATE_LIMIT_WINDOW` - окно времени в секундах

### Проблемы с кэшем

1. Проверьте подключение к Redis: `docker-compose logs redis`
2. Проверьте TTL в `.env`: `CACHE_TTL`

## 📄 Лицензия

Этот проект создан в учебных целях.

## 👤 Автор

Учебный проект для изучения backend-разработки и DevOps практик.

## 🧩 Jenkins (минимальная настройка для CI/CD с деплоем на VPS)

### Быстрый старт — запуск Jenkins через Docker Compose

Jenkins уже добавлен в `docker-compose.yml` и запускается как часть всей инфраструктуры:

```bash
# Запустить все сервисы включая Jenkins
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотреть логи Jenkins
docker-compose logs -f jenkins
```

Jenkins будет доступен по адресу: **http://localhost:8081**

#### Первоначальная настройка Jenkins

1. **Получить начальный пароль**:
   ```bash
   docker-compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
   Или просмотрите логи: `docker-compose logs jenkins | grep -i "password"`

2. **Открыть Jenkins UI**: http://localhost:8081

3. **Установить плагины**: при первом входе Jenkins предложит установить рекомендуемые плагины. Выберите **Install suggested plugins**.

4. **Создать первого администратора**: заполните форму регистрации (username, password).

5. **Установить дополнительные плагины** (если не установились автоматически):
   - Jenkins → **Manage Jenkins** → **Manage Plugins** → **Available plugins**.
   - Поищите и установите:
     - **Pipeline** (обычно уже установлен).
     - **Git** (для работы с GitHub).
     - **Docker** (для работы с Docker).
   - Перезагрузить Jenkins: http://localhost:8081/restart

---

### Архитектура развертывания (Вариант A — Pull из реестра)

1. **Build** на машине с Jenkins: `docker build` → собран образ.
2. **Push** в Docker Hub: образ залит в `docker.io/youruser/deployment_project:hash`.
3. **Deploy** на VPS: Jenkins подключается по SSH, выполняет `docker-compose pull` и `docker-compose up -d`.

### Требования

- Jenkins агент с Docker установленным.
- SSH доступ к VPS (ключ добавлен в Jenkins).
- Учётная запись Docker Hub (или другой публичный/приватный реестр).

### Параметры Pipeline

- `IMAGE_NAME` — имя образа (по умолчанию `deployment_project`).
- `REGISTRY` — адрес реестра (пример: `docker.io/youruser`). Оставьте пустым для локальной сборки.
- `PUSH_TO_REGISTRY` — если `true`, образ пушится в реестр и триггерится деплой на VPS.

### Настройка Credentials в Jenkins

#### 1. Docker Hub / Registry Credentials

1. Откройте Jenkins → **Manage Credentials** → **System** → **Global credentials**.
2. Нажмите **Add Credentials**.
3. Выберите **Username with password**.
4. Заполните:
   - **Username**: ваш Docker Hub username.
   - **Password**: ваш Docker Hub token или пароль.
   - **ID**: `DOCKERHUB_CRED` (важно, должен совпадать с `Jenkinsfile`).
5. Нажмите **Create**.

#### 2. SSH Credentials для VPS

1. Jenkins → **Manage Credentials** → **System** → **Global credentials** → **Add Credentials**.
2. Выберите **SSH Username with private key**.
3. Заполните:
   - **Username**: `root` или имя пользователя на VPS (важно совпадает с `Jenkinsfile`).
   - **Private Key**: вставьте содержимое вашего приватного SSH-ключа (например, `~/.ssh/id_rsa`).
   - **ID**: `VPS_SSH` (совпадает с `Jenkinsfile`).
4. Нажмите **Create**.

#### 3. Environment Variables для VPS

1. Jenkins → **Manage Jenkins** → **Configure System** → **Global properties** → **Environment variables**.
2. Добавьте две переменные:
   - **Name**: `VPS_HOST` → **Value**: IP-адрес или доменное имя VPS (пример: `123.45.67.89` или `vps.example.com`).
   - **Name**: `VPS_DEPLOY_PATH` → **Value**: путь к проекту на VPS (пример: `/opt/deployment_project`).
3. Нажмите **Save**.

### Создание Pipeline Job

1. Jenkins → **New Item**.
2. Введите имя: `deployment_project-build`.
3. Выберите **Pipeline**.
4. Нажмите **OK**.
5. В разделе **Pipeline**:
   - Выберите **Pipeline script from SCM**.
   - **SCM**: выберите **Git**.
   - **Repository URL**: `https://github.com/s4nrice/deployment_project.git` (ваш репозиторий).
   - **Branch**: `*/master` (или ветка по умолчанию).
   - **Script Path**: `Jenkinsfile`.
6. Нажмите **Save**.

### Пример запуска Pipeline

1. Откройте job → **Build with Parameters**.
2. Заполните параметры:
   - `IMAGE_NAME`: `deployment_project`
   - `REGISTRY`: `docker.io/youruser` (замените `youruser` на ваше имя).
   - `PUSH_TO_REGISTRY`: отметьте флажок.
3. Нажмите **Build**.

Pipeline выполнит:
- Checkout репозитория.
- Build Docker-образа с тагом `:shortGitHash`.
- Login в Docker Hub и push образа.
- SSH на VPS, pull образа, `docker-compose up -d`.

### Настройка на VPS

На VPS должны быть:
- Docker и docker-compose установлены.
- Файлы проекта в `/opt/deployment_project` (или другой путь из `VPS_DEPLOY_PATH`).
- `docker-compose.yml` с образом в формате `image: docker.io/youruser/deployment_project:latest` (или с конкретным тагом).

Пример `docker-compose.yml` на VPS:
```yaml
version: '3.8'
services:
  app:
    image: docker.io/youruser/deployment_project:latest
    ports:
      - "8888:8888"
    environment:
      - OPENWEATHER_API_KEY=your_key
    restart: unless-stopped
  redis:
    image: redis:7-alpine
    restart: unless-stopped
  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    restart: unless-stopped
```

### Отключение GitHub Actions

Если хотите полностью перейти на Jenkins, удалите или деактивируйте `.github/workflows/ci-cd.yml` через GitHub UI.

### Troubleshooting

- **SSH connection fails**: проверьте, что SSH-ключ добавлен правильно, и VPS IP/домен верны.
- **Docker login fails**: убедитесь, что `DOCKERHUB_CRED` credentials содержат правильный пароль/token.
- **docker-compose pull fails**: проверьте на VPS, что `docker login` успешен и образ доступен в реестре.

