from .views import *
from django.urls import path
from django.conf.urls import url


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("users/", UserCreate.as_view(), name="user_create"), # create user promise (username,mail,password)
    path('get_user_data/', get_user_data),
    path('list_chats/', list_chats),
    path('chat_room/<pk>', chat_room),
    path('add_chat_room/', add_chat_room),
    path('add_user_to_chat_room/', add_user_to_chat_room),
    path('search_users/', search_users),
    path("change_avatar/", change_avatar),
    # path("change_avatar/", change_avatar)
]
