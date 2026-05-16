import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.campaigns.models import Character

class CampaignConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'session_{self.session_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Отправляем текущее состояние при подключении
        await self.send_initial_state()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        payload = data.get('payload')

        if action == 'move_token':
            await self.handle_move_token(payload)
        elif action == 'chat_message':
            await self.broadcast_chat_message(payload)

    async def handle_move_token(self, payload):
        char_id = payload.get('character_id')
        x = payload.get('x')
        y = payload.get('y')
        
        await self.update_character_position(char_id, x, y)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'token_moved',
            'data': {'character_id': char_id, 'x': x, 'y': y}
        })

    async def token_moved(self, event):
        await self.send(text_data=json.dumps(event))

    async def ai_generated(self, event):
        # Пушим результат работы AI всем в комнате
        await self.send(text_data=json.dumps({
            'type': 'ai_result',
            'data': event['data']
        }))

    async def broadcast_chat_message(self, payload):
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'data': payload
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def update_character_position(self, char_id, x, y):
        Character.objects.filter(id=char_id).update(position_x=x, position_y=y)

    @database_sync_to_async
    def get_initial_state(self):
        chars = Character.objects.filter(session_id=self.session_id)
        return [{
            'id': c.id,
            'name': c.name,
            'x': c.position_x,
            'y': c.position_y,
            'color': c.image_color,
            'is_npc': c.is_npc
        } for c in chars]

    async def send_initial_state(self):
        data = await self.get_initial_state()
        await self.send(text_data=json.dumps({
            'type': 'init_state',
            'data': data
        }))