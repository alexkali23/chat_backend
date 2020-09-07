from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from .models import Chat_room, Chat_room_users, Message_chat, Profile, Message_status

from .serializers import UserSerializer, UserSerializerView, MessageSerializer, ChatsSerializer, Chat_room_users_serializer

from .views import LoginView, UserCreate, get_user_data, list_chats, chat_room, add_chat_room, add_user_to_chat_room, search_users
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class ChatTest(APITestCase):
    '''
    '''

    def setUp(self):
        print('создаю данные')
        self.user1 = User.objects.create(
            username='user_1', password='gd_gdferw_ew')
        Token.objects.create(user=self.user1)
        self.user2 = User.objects.create(
            username='user_2', password='gd_gdferw_ew')
        Token.objects.create(user=self.user2)
        self.user3 = User.objects.create(
            username='user_3', password='gd_gdferw_ew')
        Token.objects.create(user=self.user3)

        self.chat1 = Chat_room.objects.create(name='chat1')
        Chat_room_users.objects.create(user=self.user1, chat_room=self.chat1)
        Chat_room_users.objects.create(user=self.user2, chat_room=self.chat1)

        self.chat2 = Chat_room.objects.create(name='chat2')
        Chat_room_users.objects.create(user=self.user1, chat_room=self.chat2)

    def test_chat1_read(self):
        request = self.create_request('chat_room/', self.user1, 'GET')
        data = chat_room(request, self.chat1.id).data
        self.assertEquals(data['chat_room']['id'], self.chat1.id)

    def test_chat2_delete(self):
        request = self.create_request('chat_room/', self.user1, 'DELETE')
        data = chat_room(request, self.chat2.id).data
        check_chat = Chat_room.objects.filter(id=self.chat2.id).exists()
        self.assertEquals(check_chat, False)

    def test_chat1_change_name(self):
        request = self.create_request(
            'chat_room/', self.user1, 'PUT', data={'name': 'new_name'})
        data = chat_room(request, self.chat1.id).data
        self.assertEquals(data['name'], 'new_name')

    def test_create_chat(self):
        request = self.create_request(
            'add_chat_room/', self.user1, 'POST', data={'name': 'new_chat'})
        data = add_chat_room(request).data
        new_chat = Chat_room.objects.filter(id=data['id']).get()
        self.assertEquals(new_chat.name, 'new_chat')

    def test_add_user_to_chat(self):
        request = self.create_request(
            'add_user_to_chat_room/', self.user1, 'POST', data={'chat_room': '2', 'user': '2'})
        data = add_user_to_chat_room(request).data
        check_user_in_chat = Chat_room_users.objects.filter(
            chat_room=self.chat2, user=self.user2).exists()
        self.assertEquals(check_user_in_chat, True)

    def test_secure_add_user_to_chat(self):
        request = self.create_request(
            'add_user_to_chat_room/', self.user2, 'POST', data={'chat_room': '2', 'user': '3'})
        data = add_user_to_chat_room(request).data
        check_user_in_chat = Chat_room_users.objects.filter(
            chat_room=self.chat2, user=self.user3).exists()
        self.assertEquals(check_user_in_chat, False)

    def test_secure_chat_read(self):
        request = self.create_request('chat_room/', self.user3, 'GET')
        data = chat_room(request, self.chat1.id).data
        self.assertEquals(data, None)

    def create_request(self, url, user, method, data={}):
        factory = APIRequestFactory()

        if method == 'GET':
            req = factory.get
        if method == 'POST':
            req = factory.post
        if method == 'DELETE':
            req = factory.delete
        if method == 'PUT':
            req = factory.put

        return req(url, data, HTTP_AUTHORIZATION=user.auth_token.key)
