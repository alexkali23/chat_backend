from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib import auth
from datetime import datetime
from django.core import serializers
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework import views
from .models import *

from django.shortcuts import render , redirect
import json
import math
from .serializers import *

from django.db.models import Sum

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework import status


class LoginView(APIView):
    permission_classes = ()
    def post(self, request,):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key,'username':username,'avatar':user.profile.avatar.url})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer




@api_view(['GET'])
@permission_classes([permissions.AllowAny,])

def get_user_data(request):
    '''
    '''
    args = {}
    user = auth.get_user(request)
    if request.method == 'GET':
        if(request.user.is_authenticated):
            args['username'] = 'AnonymousUser'
            return Response(args)               #!!!! не законченно
        else:
            args['username'] = 'AnonymousUser'
            return Response(args)




@api_view(['GET'])
@permission_classes([permissions.AllowAny,])

def list_chats(request):
    '''
    '''
    args = {}
    user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION']).user_id
    user = User.objects.get(id=user_id)
    if request.method == 'GET':
        paginator = PageNumberPagination()
        paginator.page_size = 20
        list_article = Chat_room.objects.filter(chat_room_users__user_id = user.id)
        result_page = paginator.paginate_queryset(list_article, request)
        serializer = ChatsSerializer(result_page, many=True,context={'user': user})
        return paginator.get_paginated_response(serializer.data)




@api_view(['GET','PUT','DELETE'])
@permission_classes([permissions.AllowAny,])
def chat_room(request,pk):
    '''

    '''
    user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION']).user_id
    user = User.objects.get(id=user_id)
    try:
        chat = Chat_room.objects.get(id=pk)
        try: # проверяем наличие доступа к данным у пользователя
            Chat_room_users.objects.get(user = user, chat_room = chat)
        except Chat_room_users.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)#нет доступа
    except Chat_room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        list_message = Messege_chat.objects.filter(chat_room = chat)[:20]
        messages = MessageSerializer(list_message,  many=True).data
        chat = ChatsSerializer(chat,context={'user': user}).data
        return Response({'messages': messages,'chat_room':chat})

    if request.method == 'PUT': # не используется
        serializer = ChatsSerializer(chat, data=request.data,context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)









@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def add_chat_room(request):
    user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION']).user_id
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        serializer = ChatsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user_id'] = user.id
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def add_user_to_chat_room(request):

    user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION']).user_id
    user = User.objects.get(id=user_id)

    chat_room = Chat_room.objects.get(id = request.data['chat_room'])
    another_user = User.objects.get(id = request.data['user'])

    try: # проверяем наличие доступа к данным у пользователя
        Chat_room_users.objects.get(user = user, chat_room = chat_room)
    except Chat_room_users.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)#нет доступа

    if request.method == 'POST':
        serializer = Chat_room_users_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def search_users(request):

    user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION']).user_id
    user = User.objects.get(id=user_id)
    
    user_list =  User.objects.filter(username__contains=request.data['text'])[:20]
    serializer = UserSerializerView(user_list, many=True)
    return Response(serializer.data)
    



from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser




@api_view(['POST'])
@permission_classes([permissions.AllowAny,])
def change_avatar(request):
    print('load_file')
    return Response({}, 200)








