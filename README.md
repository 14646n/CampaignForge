# CampaignForge

Платформа для управления настольными ролевыми играми (НРИ) с AI-помощником.

## Требования

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Ollama (для AI-функций)

### Установка Ollama

**Linux/macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama2
```

**Windows:**
Скачайте с https://ollama.com/download/windows

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
# Linux/macOS:
source venv/bin/activate
# Windows (Git Bash):
source ../venv/Scripts/activate
# Windows (CMD/PowerShell):
venv\Scripts\activate

python manage.py runserver
```

Сервер запустится на `http://localhost:8000`

#### Терминал 2 - Frontend (Vite)

```bash
cd frontend
npm run dev
```

Сервер запустится на `http://localhost:5173`

#### Терминал 3 - Celery Worker (для AI-задач)

```bash
cd backend
# Linux/macOS:
source venv/bin/activate
# Windows (Git Bash):
source ../venv/Scripts/activate
# Windows (CMD/PowerShell):
venv\Scripts\activate

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
4. **Добавьте персонажей** через админку или API
5. **Откройте карту** по адресу `http://localhost:5173/map/{session_id}`
6. **Используйте чат с AI** для генерации NPC, встреч и описаний

## Быстрый старт (Windows + Git Bash)

```bash
# Терминал 1 - Backend
cd /d/dnd/CampaignForge/backend
source ../venv/Scripts/activate
python manage.py runserver

# Терминал 2 - Frontend  
cd /d/dnd/CampaignForge/frontend
npm run dev

# Терминал 3 - Celery
cd /d/dnd/CampaignForge/backend
source ../venv/Scripts/activate
celery -A config worker --loglevel=info
```

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
## Что нового в этой версии

### UI Компоненты
- **ChatInterface.vue** - компонент чата с AI Dungeon Master
  - Отправка сообщений через WebSocket
  - Быстрые действия для создания NPC, встреч, локаций и лута
  - Индикатор набора текста AI
  - История сообщений с временными метками

### BattleMap улучшения
- Интегрированный чат рядом с картой
- Модальное окно для отображения результатов AI
- Адаптивный дизайн с боковой панелью

### Store улучшения
- Конвертирован `campaign.js` в `campaign.ts` с полной типизацией
- Добавлены интерфейсы: Character, Session, AIMessage
- Методы для работы с AI сообщениями

### Роутер
- Добавлен роут для `/campaigns`
- Добавлен роут для `/campaign/:id`
- Убран жесткий редирект на сессию ID=1
- Главная страница теперь ведет на HomeView
