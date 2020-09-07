from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from api.models import Chat_room, Chat_room_users, Message_chat, Profile, Message_status
from urllib.parse import parse_qs
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.serializers import UserSerializer, UserSerializerView, MessageSerializer, ChatsSerializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        token = parse_qs(self.scope["query_string"].decode("utf8"))["token"][0]
        user_id = Token.objects.get(key=token).user_id
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        self.user = User.objects.get(id=user_id)
        self.chat = Chat_room.objects.get(id=self.room_name)

        chat_room_users = Chat_room_users.objects.filter(
            user=self.user, chat_room=self.chat)
        if chat_room_users.exists() == False:
            # нет доступа #правильная обработка ошибок?
            raise DenyConnection("Нет доступа")

        Message_status.objects.filter(
            user=self.user, message__chat_room=self.chat, is_read=False).update(is_read=True)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['method'] == 'ADD_MESSAGE':

            text_data_json['user'] = self.user.id  # добовляем данные
            text_data_json['chat_room'] = self.chat.id
            serializer = MessageSerializer(data=text_data_json)

            if serializer.is_valid():
                print('добовляю сообщение')
                serializer.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'data': serializer.data,
                        'type': 'chat_message',
                        'method': 'ADD_MESSAGE',
                    }
                )
        if text_data_json['method'] == 'REDACT_MESSAGE':

            text_data_json['user'] = self.user.id  # добовляем данные
            text_data_json['chat_room'] = self.chat.id

            message = Message_chat.objects.filter(
                id=text_data_json['pk'], user=self.user)
            if message.exists() == False:
                raise DenyConnection("Нет доступа")  # нет доступа
            else:
                message = message.get()

            serializer = MessageSerializer(message, data=text_data_json)
            if serializer.is_valid():
                serializer.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'data': serializer.data,
                        'type': 'chat_message',
                        'method': 'REDACT_MESSAGE',
                    }
                )
        if text_data_json['method'] == 'DELETE_MESSAGE':

            message = Message_chat.objects.filter(
                id=text_data_json['pk'], user=self.user)
            if message.exists() == False:
                raise DenyConnection("Нет доступа")  # нет доступа
            else:
                message = message.get()

            message.delete()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'data': {'id': text_data_json['pk']},
                    'type': 'chat_message',
                    'method': 'DELETE_MESSAGE',
                }
            )

        # Receive message from room group

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'method': event['method'],
            'data': event['data']
        }))


class UserPersonalConsumer(WebsocketConsumer):
    def connect(self):
        print('personal socket')
        token = parse_qs(self.scope["query_string"].decode("utf8"))["token"][0]
        user_id = Token.objects.get(key=token).user_id
        self.room_name = user_id
        self.room_group_name = 'user_%s' % user_id

        self.user = User.objects.get(id=user_id)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def send_data(self, event):
        self.send(text_data=json.dumps({
            'method': event['method'],
            'data': event['data'],
            'count_unread_message': event['count_unread_message'],
        }))
