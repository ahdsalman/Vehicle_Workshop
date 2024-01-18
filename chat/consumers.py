from userapp.models import User
from channels.layers import get_channel_layer
import json
from channels.generic.websocket import AsyncWebsocketConsumer,AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from userside.models import ServiceBooking

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    
    @database_sync_to_async
    def create_message(self, message, username, room_name):
        try:
            booking_id = int(room_name)
            
          
            booking = ServiceBooking.objects.get(id=booking_id)

            message_obj = Message.objects.create(
                room_name=booking, 
                username=username,
                message=message
            )
            return message_obj
        except ServiceBooking.DoesNotExist:
            return None
        except ValueError:

            return None

        except Exception as e:
            print(f"Error creating Message: {e}")
            return None

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        message = data['message']
        username = data['username']
        room_name = self.room_name

        message_obj = await self.create_message(message, username, room_name)
        # if message_obj is not None:
        try:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message_obj.message,
                    'username': message_obj.username,
                    'timestamp': str(message_obj.timestamp),
                }
            )
        except Exception as e:
            print("Failed to create Message object.")
            return await self.send_default_message(self)
        
    async def send_default_message(self, default_message):
        default_message = "An error occurred. Please check your room or try again later."
        await self.send(text_data=json.dumps({
            'message': default_message,
             }))

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
        }))


