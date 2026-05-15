import os
import sys

# Структура проекта и содержимое файлов
PROJECT_STRUCTURE = {
    ".env": """DEBUG=True
SECRET_KEY=django-insecure-local-dev-key-change-me
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=campaignforge
DB_USER=user
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/0

# AI Configuration (Ollama Local)
GEMINI_API_KEY=
OLLAMA_BASE_URL=http://host.docker.internal:11434

CORS_ALLOWED_ORIGINS=http://localhost:5173
""",

    "docker-compose.yml": """version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_/var/lib/postgresql/data
    environment:
      POSTGRES_DB: campaignforge
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - .env
    extra_hosts:
      - "host.docker.internal:host-gateway"

  celery_worker:
    build: ./backend
    command: celery -A config worker --loglevel=info --pool=solo
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    env_file:
      - .env
    extra_hosts:
      - "host.docker.internal:host-gateway"

  frontend:
    build: ./frontend
    command: npm run dev -- --host
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000

volumes:
  postgres_:
""",

    "backend/requirements.txt": """Django==5.0.6
djangorestframework==3.15.1
django-cors-headers==4.3.1
channels==4.1.0
channels-redis==4.2.0
daphne==4.1.0
celery==5.3.6
redis==5.0.4
psycopg2-binary==2.9.9
python-dotenv==1.0.1
pydantic==2.7.1
requests==2.31.0
pytest==8.2.0
pytest-django==4.8.0
""",

    "backend/Dockerfile": """FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000
""",

    "backend/config/__init__.py": "",
    
    "backend/config/settings.py": """import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'apps.core',
    'apps.campaigns',
    'apps.ai_engine',
    'apps.realtime',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://host.docker.internal:11434')
""",

    "backend/config/asgi.py": """import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from config.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
""",

    "backend/config/routing.py": """from django.urls import re_path
# Placeholder for WebSocket routes
websocket_urlpatterns = []
""",

    "backend/config/urls.py": """from django.contrib import admin
from django.urls import path
urlpatterns = [
    path('admin/', admin.site.urls),
]
""",

    "backend/config/celery.py": """import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
""",

    "backend/config/wsgi.py": """import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
""",

    "backend/manage.py": """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",

    # Apps Init Files
    "backend/apps/__init__.py": "",
    "backend/apps/core/__init__.py": "",
    "backend/apps/core/apps.py": """from django.apps import AppConfig
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
""",
    "backend/apps/campaigns/__init__.py": "",
    "backend/apps/campaigns/apps.py": """from django.apps import AppConfig
class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.campaigns'
""",
    "backend/apps/ai_engine/__init__.py": "",
    "backend/apps/ai_engine/apps.py": """from django.apps import AppConfig
class AiEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_engine'
""",
    "backend/apps/realtime/__init__.py": "",
    "backend/apps/realtime/apps.py": """from django.apps import AppConfig
class RealtimeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.realtime'
""",

    # Models
    "backend/apps/campaigns/models.py": """from django.db import models
from django.contrib.auth.models import User

class Campaign(models.Model):
    name = models.CharField(max_length=255)
    dm = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dm_campaigns')
    players = models.ManyToManyField(User, related_name='player_campaigns', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Session(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    map_state = models.JSONField(default=dict, blank=True) 

    def __str__(self):
        return f"{self.campaign.name} - {self.title}"

class Character(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='characters')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    data = models.JSONField(default=dict) 
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    is_npc = models.BooleanField(default=False)

class AIMessage(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='ai_logs')
    prompt = models.TextField()
    response_text = models.TextField()
    response_json = models.JSONField(null=True, blank=True)
    generated_image_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
""",

    # AI Tasks (OLLAMA INTEGRATION)
    "backend/apps/ai_engine/tasks.py": """from celery import shared_task
from django.core.cache import cache
from pydantic import BaseModel, ValidationError
import hashlib
import json
import requests
import os

class NPCData(BaseModel):
    name: str
    race: str
    class_name: str
    level: int
    description: str
    stats: dict

class EncounterData(BaseModel):
    location: str
    enemies: list[dict]
    loot: list[str]
    narrative_hook: str

@shared_task(bind=True, max_retries=3)
def generate_ai_content(self, session_id: int, prompt: str, content_type: str):
    cache_key = f"ai_gen:{hashlib.md5((prompt + content_type).encode()).hexdigest()}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    schema_map = {
        'npc': NPCData,
        'encounter': EncounterData
    }
    target_schema = schema_map.get(content_type)
    if not target_schema:
        raise ValueError(f"Unknown content type: {content_type}")

    gemini_key = os.getenv('GEMINI_API_KEY')
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://host.docker.internal:11434')

    try:
        result_json = {}
        
        if gemini_key:
            # Gemini Logic (skipped if key empty)
            from google import generativeai
            generativeai.configure(api_key=gemini_key)
            model = generativeai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(f"Generate D&D {content_type}: {prompt}")
            result_json = json.loads(response.text)
        else:
            # OLLAMA FALLBACK LOGIC
            print(f"Using Ollama at {ollama_url} for generation...")
            ollama_prompt = f"""You are a D&D 5e assistant. Output ONLY valid JSON matching this schema: {target_schema.model_json_schema()}.
            Request: {prompt}"""
            
            payload = {
                "model": "llama3", 
                "prompt": ollama_prompt,
                "stream": False,
                "format": "json" 
            }
            
            response = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            result_text = response.json().get('response', '')
            result_json = json.loads(result_text)

        validated_data = target_schema(**result_json)
        cache.set(cache_key, validated_data.model_dump(), timeout=3600)
        return validated_data.model_dump()

    except Exception as e:
        print(f"AI Generation Error: {e}")
        raise self.retry(exc=e, countdown=5)

def generate_image_url(prompt: str, seed: int = None) -> str:
    import random
    if seed is None: seed = random.randint(1000, 9999)
    safe_prompt = requests.utils.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
""",

    # Frontend Package
    "frontend/package.json": """{
  "name": "campaign-forge-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.8",
    "konva": "^9.3.1",
    "pinia": "^2.1.7",
    "vue": "^3.4.27",
    "vue-konva": "^3.0.2",
    "vue-router": "^4.3.2"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.4",
    "typescript": "^5.4.5",
    "vite": "^5.2.11",
    "vue-tsc": "^2.0.19"
  }
}
""",

    "frontend/Dockerfile": """FROM node:18-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
""",

    "frontend/vite.config.ts": """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
  },
})
""",

    "frontend/tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
""",
    "frontend/tsconfig.node.json": """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
""",
    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CampaignForge AI</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
""",
    "frontend/src/main.ts": """import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
""",
    "frontend/src/App.vue": """<template>
  <div id="app">
    <nav style="padding: 1rem; background: #333; color: white;">
      <router-link to="/" style="color: white; margin-right: 1rem;">Home</router-link>
      <router-link to="/campaigns" style="color: white;">Campaigns</router-link>
    </nav>
    <main style="padding: 1rem;">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
body { margin: 0; font-family: sans-serif; }
</style>
""",
    "frontend/src/router/index.ts": """import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomeView },
    { 
      path: '/campaigns', 
      component: () => import('../views/CampaignView.vue') 
    },
  ],
})

export default router
""",
    "frontend/src/views/HomeView.vue": """<template>
  <h1>Welcome to CampaignForge AI</h1>
  <p>Your local D&D Assistant powered by Ollama.</p>
  <div v-if="status">{{ status }}</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const status = ref('Checking backend connection...')

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/admin/')
    if(res.ok || res.status === 401) status.value = 'Backend Connected! (Check /admin)'
  } catch (e) {
    status.value = 'Backend offline. Start Docker.'
  }
})
</script>
""",
    "frontend/src/views/CampaignView.vue": """<template>
  <div>
    <h1>Campaign Dashboard</h1>
    <p>AI Integration Ready (Ollama)</p>
    <div class="card">
      <h3>Generate NPC</h3>
      <input v-model="prompt" placeholder="Describe NPC..." style="width: 100%; padding: 8px;" />
      <button @click="generateNPC" :disabled="loading" style="margin-top: 10px; padding: 8px 16px;">
        {{ loading ? 'Generating...' : 'Generate with Ollama' }}
      </button>
      <pre v-if="result" style="background: #f4f4f4; padding: 10px; margin-top: 10px;">{{ result }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// Mock function for now until API endpoints are fully wired in next steps
const prompt = ref('')
const loading = ref(false)
const result = ref(null)

const generateNPC = async () => {
  loading.value = true
  // In next step we will connect this to the actual DRF endpoint
  setTimeout(() => {
    result.value = { name: "Test NPC", race: "Human", note: "Backend logic coming in next file set!" }
    loading.value = false
  }, 1000)
}
</script>
""",
    "frontend/src/stores/campaign.ts": """import { defineStore } from 'pinia'
export const useCampaignStore = defineStore('campaign', {
  state: () => ({ campaigns: [] }),
  actions: {}
})
""",
    "frontend/src/stores/map.ts": """import { defineStore } from 'pinia'
export const useMapStore = defineStore('map', {
  state: () => ({ characters: [] }),
  actions: {}
})
""",
    "frontend/src/stores/ai.ts": """import { defineStore } from 'pinia'
export const useAIStore = defineStore('ai', {
  state: () => ({ generating: false }),
  actions: {}
})
""",
}

def create_files():
    print("🚀 Starting Project Generation...")
    for filepath, content in PROJECT_STRUCTURE.items():
        full_path = os.path.join(os.getcwd(), filepath)
        directory = os.path.dirname(full_path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {filepath}")

    print("\n✨ Project structure generated successfully!")
    print("\n👉 Next steps:")
    print("1. git checkout -b dev/mvp-core")
    print("2. git add .")
    print("3. git commit -m 'feat: Initial MVP structure with Ollama support'")
    print("4. docker-compose up --build")

if __name__ == "__main__":
    create_files()
