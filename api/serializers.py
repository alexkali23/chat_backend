from rest_framework.authtoken.models import Token
from .models import Chat_room, Chat_room_users, Message_chat, Profile, Message_status
from django.contrib.auth.models import User
from rest_framework import serializers

#UserSerializer, UserSerializerView, MessageSerializer, ChatsSerializer, Chat_room_users_serializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user


# вероятно вожно обойтись одним сериализатором
class UserSerializerView(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id', 'avatar')

    avatar = serializers.SerializerMethodField('get_avatar')

    def get_avatar(self, obj):
        return obj.profile.avatar.url


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message_chat
        fields = '__all__'
    test = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField(source='get_username', required=False)
    avatar = serializers.ReadOnlyField(source='get_avatar', required=False)


class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_room
        fields = ['name', 'id', 'last_message', 'count_unread_messages']

    last_message = serializers.SerializerMethodField('get_last_message')
    count_unread_messages = serializers.SerializerMethodField(
        'get_count_unread_messages')

    def get_last_message(self, obj):
        message = obj.last_message()
        if message == None:
            return None
        else:
            serializer = MessageSerializer(message)
            return serializer.data

    def get_count_unread_messages(self, obj):
        if self.context == {}:
            return 0
        chat_room = obj
        user = self.context['user']
        return Message_status.objects.filter(user=user, message__chat_room=chat_room, is_read=False).count()

    def create(self, validated_data):

        chat = Chat_room(
            name=validated_data['name']
        )
        chat.save()

        chat_room_users = Chat_room_users(
            chat_room=chat, user_id=validated_data['user_id'])
        chat_room_users.save()
        return chat


class Chat_room_users_serializer(serializers.ModelSerializer):
    class Meta:
        model = Chat_room_users
        fields = '__all__'
