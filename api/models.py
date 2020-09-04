from django.db import models
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save

import datetime




class Chat_room(models.Model):
    class Meta():
        db_table = 'chat_room'
    name = models.CharField(verbose_name='имя',max_length=100,default='')
    def last_message(self):
        message = Messege_chat.objects.filter(chat_room = self).order_by('-id')[:1]
        if (message.exists()):
            return message.get()
        else:
            return None


class Chat_room_users(models.Model):
    class Meta():
        db_table = 'Chat_room_users'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(Chat_room, on_delete=models.CASCADE)
    is_muted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    

class Messege_chat(models.Model):
    class Meta():
        db_table = 'message'
    user = models.ForeignKey(User,verbose_name='message', on_delete=models.CASCADE)
    chat_room = models.ForeignKey(Chat_room, on_delete=models.CASCADE)
    text = models.CharField(verbose_name='text',max_length=100,default='')
    created_date = models.DateTimeField( auto_now_add=True)
    update_date = models.DateTimeField( auto_now_add=True)
    def get_username(self):
        return self.user.username
    def get_avatar(self):
        return self.user.profile.avatar.url





class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='img_user', verbose_name='Изображение',default='img_user/standart.png')
    def __unicode__(self):
        return self.user
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'



class Message_status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Messege_chat, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)




@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    


#уведомления



from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import MessageSerializer , ChatsSerializer





@receiver(post_save, sender=Messege_chat)
def new_message_chat(sender, instance,created, **kwargs):
    channel_layer = get_channel_layer()
    users = Chat_room_users.objects.filter(chat_room = instance.chat_room)
    message = instance
    if created or instance.chat_room.last_message() == instance:
        for i in users:
            if i.user == instance.user:
                continue


            message_status = Message_status(message = instance,user = i.user)
            message_status.save()


            serializer = MessageSerializer(message)
            async_to_sync(channel_layer.group_send)('user_%s' % i.user.id, {
                'method': "NEW_MESSAGE",
                'type': 'send_data',
                'data': serializer.data,
                'count_unread_message': Message_status.objects.filter(user = i.user ,message__chat_room = instance.chat_room,is_read = False).count(),
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



