from rest_framework import serializers
from .models import Campaign, Session, Character

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    characters = CharacterSerializer(many=True, read_only=True)
    class Meta:
        model = Session
        fields = '__all__'

class CampaignSerializer(serializers.ModelSerializer):
    sessions = SessionSerializer(many=True, read_only=True)
    class Meta:
        model = Campaign
        fields = '__all__'