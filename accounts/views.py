from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserListserializer,
    Userserializer,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

import random



class UserView(APIView):
    @login_required
    def get(self, request, user_pk=None):
        if user_pk: # pk를 받을 시에는 단일 유저 조회
            user = get_object_or_404(get_user_model(), pk=user_pk)
            serializer = Userserializer(user)
            return Response(serializer.data)
        # pk를 안받을 시에는 전체 유저 목록 조회
        users = get_list_or_404(get_user_model())
        serializer = UserListserializer(users, many=True)
        return Response(serializer.data)
    
    # 계정 생성
    def post(self, request):
        prefix_list = ['활발한', '귀여운', '구슬픈', '애잔한', '멋있는', '즐거운', '침착한', '조용한', '활기찬', '쾌활한', '용감한', '진지한']
        suffix_list = ['쥐돌이', '송아지', '호랑이', '토깽이', '용용이', '뱀뱀이', '망아지', '양양이', '원숭이', '병아리', '댕댕이', '꿀꿀이']
        auto_created_nickname = prefix_list[random.randint(0, 13)] + suffix_list[random.randint(0, 13)] + str(random.randint(1, 1000))
        serializer = Userserializer(data=request.POST, nickname=auto_created_nickname)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def put(self, request):
        user = request.user
        serializer = Userserializer()
        

class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer