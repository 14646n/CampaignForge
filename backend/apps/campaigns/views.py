from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Campaign, Session, Character
from .serializers import CampaignSerializer, SessionSerializer, CharacterSerializer
from apps.ai_engine.tasks import generate_ai_content

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    @action(detail=True, methods=['post'])
    def create_session(self, request, pk=None):
        campaign = self.get_object()
        session = Session.objects.create(campaign=campaign, title=request.data.get('title', 'New Session'))
        return Response(SessionSerializer(session).data)

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @action(detail=True, methods=['post'])
    def generate_ai(self, request, pk=None):
        session = self.get_object()
        prompt = request.data.get('prompt')
        content_type = request.data.get('type', 'npc')
        
        if not prompt:
            return Response({'error': 'Prompt required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Запускаем Celery задачу асинхронно
        task = generate_ai_content.delay(session.id, prompt, content_type)
        
        return Response({'status': 'processing', 'task_id': task.id})

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer