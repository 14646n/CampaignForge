from django.contrib import admin
# Убрали MapSnapshot из импорта
from .models import Campaign, Session, Character, AIMessage

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'dm', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('players',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign', 'is_active', 'created_at')
    list_filter = ('is_active', 'campaign')
    readonly_fields = ('map_state',)

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'session', 'user', 'is_npc')
    list_filter = ('is_npc', 'session')
    search_fields = ('name',)

@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'status', 'created_at')
    list_filter = ('status', 'session')
    readonly_fields = ('prompt', 'response_text', 'response_json')