from django.db import models
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
