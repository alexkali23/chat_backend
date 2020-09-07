from django.db import models
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save

import datetime


#Chat_room, Chat_room_users, Message_chat, Profile, Message_status


class Chat_room(models.Model):
    class Meta():
        db_table = 'chat_room'
    name = models.CharField(verbose_name='имя', max_length=100, default='')

    def last_message(self):
        message = Message_chat.objects.filter(chat_room=self)
        if (message.exists()):
            return message.last()
        else:
            return None


class Chat_room_users(models.Model):
    class Meta():
        db_table = 'Chat_room_users'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey('api.Chat_room', on_delete=models.CASCADE)
    is_muted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)


class Message_chat(models.Model):

    class Meta():
        db_table = 'message'
    user = models.ForeignKey(
        User, verbose_name='message', on_delete=models.CASCADE)
    chat_room = models.ForeignKey('api.Chat_room', on_delete=models.CASCADE)
    text = models.CharField(verbose_name='text', max_length=100, default='')
    created_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    @property
    def test(self):
        return self.user.username

    def get_username(self):
        return self.user.username

    def get_avatar(self):
        return self.user.profile.avatar.url


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='img_user', verbose_name='Изображение', default='img_user/standart.png')

    def __unicode__(self):
        return self.user


class Message_status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey('api.Message_chat', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



