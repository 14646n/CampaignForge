# CampaignForge

Платформа для управления настольными ролевыми играми (НРИ) с AI-помощником.

## Требования

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

## Установка и запуск (без Docker)

### 1. Подготовка окружения

#### База данных PostgreSQL

Создайте базу данных и пользователя:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE campaignforge;
CREATE USER user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE campaignforge TO user;
\q
```

#### Redis

Установите и запустите Redis:

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Скачайте с https://github.com/microsoftarchive/redis/releases или используйте WSL.

### 2. Настройка Backend

```bash
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py migrate

# Создание суперпользователя (для доступа к админке)
python manage.py createsuperuser
```

### 3. Настройка Frontend

```bash
cd frontend

# Установка зависимостей
npm install
```

### 4. Запуск серверов

Вам потребуется **три терминала**:

#### Терминал 1 - Backend (Django)

```bash
cd backend
source venv/bin/activate  # или venv\Scripts\activate на Windows
python manage.py runserver
```

Сервер запустится на `http://localhost:8000`

#### Терминал 2 - Frontend (Vite)

```bash
cd frontend
npm run dev
```

Сервер запустится на `http://localhost:5173`

#### Терминал 3 - Celery Worker (опционально, для фоновых задач)

```bash
cd backend
source venv/bin/activate  # или venv\Scripts\activate на Windows
celery -A config worker --loglevel=info
```

### 5. Доступ к приложению

1. Откройте браузер и перейдите на `http://localhost:5173`
2. Для доступа к админке: `http://localhost:8000/admin`
3. Войдите под созданным суперпользователем

### 6. Первые шаги

1. **Войдите в админку** (`http://localhost:8000/admin`)
2. **Создайте компанию** в разделе Campaigns → Companies
3. **Создайте сессию** в разделе Campaigns → Sessions
4. **Вернитесь на фронтенд** (`http://localhost:5173`) и начните работу

## Конфигурация

Основной файл конфигурации: `.env` в корне проекта

```env
DEBUG=True
SECRET_KEY=django-insecure-local-dev-key-change-me
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=campaignforge
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

CORS_ALLOWED_ORIGINS=http://localhost:5173
```

## Устранение проблем

### Ошибка подключения к базе данных
Убедитесь, что PostgreSQL запущен и параметры в `.env` верны.

### Ошибка подключения к Redis
Проверьте, что Redis запущен:
```bash
redis-cli ping
# Должен вернуть: PONG
```

### Проблемы с CORS
Если фронтенд не может подключиться к бэкенду, проверьте `CORS_ALLOWED_ORIGINS` в `.env`.

## Разработка

### Запуск тестов

```bash
cd backend
pytest
```

### Сборка фронтенда для продакшена

```bash
cd frontend
npm run build
```

## Лицензия

MIT
