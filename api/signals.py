# уведомления
from .serializers import MessageSerializer, ChatsSerializer
from .models import Chat_room, Chat_room_users, Message_chat, Profile, Message_status
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=Message_chat)
def new_message_chat(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    users = Chat_room_users.objects.filter(chat_room=instance.chat_room)
    message = instance
    if created or instance.chat_room.last_message() == instance:
        for i in users:
            if i.user == instance.user:
                continue

            message_status = Message_status(message=instance, user=i.user)
            message_status.save()

            serializer = MessageSerializer(message)
            async_to_sync(channel_layer.group_send)('user_%s' % i.user.id, {
                'method': "NEW_MESSAGE",
                'type': 'send_data',
                'data': serializer.data,
                'count_unread_message': Message_status.objects.filter(user=i.user, message__chat_room=instance.chat_room, is_read=False).count(),
            })


@receiver(post_save, sender=Chat_room_users)
def new_chat_room(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    chat_room = instance.chat_room
    serializer = ChatsSerializer(chat_room)
    async_to_sync(channel_layer.group_send)('user_%s' % instance.user.id, {
        'method': "NEW_CHAT",
        'type': 'send_data',
        'data': serializer.data,
        'count_unread_message': 0
    })