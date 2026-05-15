from celery import shared_task
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
            schema_str = json.dumps(target_schema.model_json_schema()) # Превращаем схему в строку JSON
            ollama_prompt = (
                "You are a D&D 5e assistant. Output ONLY valid JSON matching this schema: " 
                + schema_str + 
                ". Request: " + prompt
            )
            
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
