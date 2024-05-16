from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseNotAllowed
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserListserializer,
    Userserializer,
    UsercreateSerializer,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

# Github Social Login용
# from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from dj_rest_auth.registration.views import SocialLoginView

import random



class UserView(APIView):
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
        auto_created_nickname = prefix_list[random.randint(0, 12)] + ' ' + suffix_list[random.randint(0, 12)] + str(random.randint(1, 1000))
        serializer = UsercreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(nickname=auto_created_nickname)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # 계정 수정
    def put(self, request, user_pk):
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if request.user == user or request.user.is_admin:
            if request.data.get('password'):
                password = request.data.pop('password')
                user.set_password(password)
            serializer = Userserializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'msg': "you can\'t edit this account"}, status=status.HTTP_403_FORBIDDEN)
        
    # 계정 삭제 OR 비활성화    
    def delete(self, request, user_pk=None, delete_force=None):
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if delete_force and request.user.is_admin:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.user == user or request.user.is_admin:
            user.is_active = False
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)  
            
        
# 로그인 시 토큰 발급
class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

# 친구 추가&삭제 기능. symmetrical=True 라 한명만 삭제해도 일방적으로 삭제됨. Channels 라이브러리를 이용한 websocket 구현? 되겠?
class FriendView(APIView):
    def post(self, request, user_pk):
        me = request.user
        you = get_object_or_404(get_user_model(), pk=user_pk)
        if me != you:
            is_friend = me.friends.filter(pk=user_pk).exists()
            if is_friend:
                me.friends.remove(you)
            else:
                me.friends.add(you)
        else:
            return HttpResponseForbidden('')
        return Response({'msg': f'{ "friend deleted" if is_friend else "friend added"}', 'is_friend': not is_friend})
                
            
# Github 로그인용
# class GitHubLogin(SocialLoginView):
#     adapter_class = GitHubOAuth2Adapter
#     callback_url = CALLBACK_URL_YOU_SET_ON_GITHUB
#     client_class = OAuth2Client