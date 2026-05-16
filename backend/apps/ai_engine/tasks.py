from celery import shared_task
from django.core.cache import cache
from apps.campaigns.models import AIMessage, Session
import requests
import json
import hashlib
from pydantic import BaseModel, ValidationError

# --- Схемы валидации (Pydantic) ---
class NPCData(BaseModel):
    name: str
    race: str
    class_name: str
    level: int
    description: str
    stats: dict

class EncounterData(BaseModel):
    location: str
    enemies: list
    loot: list
    narrative_hook: str

@shared_task(bind=True, max_retries=3)
def generate_ai_content(self, session_id: int, prompt: str, content_type: str):
    """
    Генерирует контент через локальную Ollama.
    """
    # 1. Проверка кэша (опционально)
    cache_key = f"ai_gen:{hashlib.md5((prompt + content_type).encode()).hexdigest()}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    # 2. Выбор схемы
    schema_map = {
        'npc': NPCData,
        'encounter': EncounterData
    }
    target_schema = schema_map.get(content_type)
    if not target_schema:
        raise ValueError(f"Unknown content type: {content_type}")

    # 3. Формирование промпта для Ollama
    # Мы просим модель вернуть ТОЛЬКО JSON
    schema_str = json.dumps(target_schema.model_json_schema())
    system_prompt = (
        "You are a D&D 5e assistant. Output ONLY valid JSON matching this schema. "
        "Do not include markdown formatting or explanations. "
        f"Schema: {schema_str}"
    )
    
    full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

    try:
        # 4. Запрос к локальной Ollama
        # URL берется из settings, по умолчанию http://localhost:11434
        from django.conf import settings
        ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        
        payload = {
            "model": "llama3",  # Убедитесь, что у вас скачана эта модель!
            "prompt": full_prompt,
            "stream": False,
            "format": "json"    # Важно: заставляет Ollama возвращать JSON
        }
        
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        
        result_text = response.json().get('response', '')
        
        # Очистка от возможных маркдаун обёрток ```json ... ```
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip("```").strip()

        result_json = json.loads(result_text)

        # 5. Валидация через Pydantic
        validated_data = target_schema(**result_json)
        final_data = validated_data.model_dump()

        # 6. Сохранение в БД
        AIMessage.objects.create(
            session_id=session_id,
            prompt=prompt,
            response_text=json.dumps(final_data, ensure_ascii=False),
            response_json=final_data,
            status='completed'
        )

        # 7. Отправка результата в WebSocket группу сессии
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        group_name = f'session_{session_id}'
        
        async_to_sync(channel_layer.group_send)(group_name, {
            'type': 'ai_generated',
            'data': {
                'type': content_type,
                'content': final_data,
                'message': f"Generated {content_type}: {final_data.get('name', 'Encounter')}"
            }
        })

        return final_data

    except requests.exceptions.RequestException as e:
        # Если Ollama не отвечает
        print(f"Ollama connection error: {e}")
        # Создаем запись об ошибке
        AIMessage.objects.create(
            session_id=session_id,
            prompt=prompt,
            response_text=f"Error connecting to Ollama: {str(e)}",
            status='failed'
        )
        raise self.retry(exc=e, countdown=5)
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Validation error: {e}")
        AIMessage.objects.create(
            session_id=session_id,
            prompt=prompt,
            response_text="Invalid JSON received from AI",
            status='failed'
        )
        raise self.retry(exc=e, countdown=5)