from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseNotAllowed, QueryDict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserListserializer,
    Userserializer,
    UsercreateSerializer,
    UserUpdateSerializer,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings

from dj_rest_auth.views import LoginView
from dj_rest_auth.models import get_token_model
from dj_rest_auth.utils import jwt_encode
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
    
    # 계정 생성: 확인 완료
    def post(self, request):
        prefix_list = ['활발한', '귀여운', '구슬픈', '애잔한', '멋있는', '즐거운', '침착한', '조용한', '활기찬', '쾌활한', '용감한', '진지한']
        suffix_list = ['쥐돌이', '송아지', '호랑이', '토깽이', '용용이', '뱀뱀이', '망아지', '양양이', '원숭이', '병아리', '댕댕이', '꿀꿀이']
        auto_created_nickname = prefix_list[random.randint(0, 12)] + ' ' + suffix_list[random.randint(0, 12)] + str(random.randint(1, 1000))
        datas = request.data.dict()
        datas['nickname'] = auto_created_nickname
        serializer = UsercreateSerializer(data=datas)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # 계정 수정: 장르 변경 제외 확인 완료
    def put(self, request, user_pk):
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if request.user == user or request.user.is_admin: # 수정 대상이 유저 본인이거나 관리자일 경우에만 실행
            genres = request.data.get('genres')
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                if request.data.get('password'): # 변경 요청 중 password가 있다면, password는 별도로 처리 후 변경
                    password = request.data.get('password')
                    user.set_password(password)
                serializer.save()
                if genres: # 변경 요청 중 장르 변경이 있다면(없을 시 genres = None 임)
                    for genre in genres: # genres 안에는 genre명과 대응되는 숫자가 들어있음
                        if genre > 0:
                            user.recommend_genre.add(genre)
                        else:
                            user.recommend_genre.remove(genre)

                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'msg': "you can\'t edit this account"}, status=status.HTTP_403_FORBIDDEN)
        
    # 계정 삭제 OR 비활성화    
    def delete(self, request, user_pk=None, delete_force=None):
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if delete_force and request.user.is_admin: # 삭제 주체가 관리자일 경우에만 실행
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.user == user or request.user.is_admin: # 삭제 주체가 대상 본인이거나 관리자일 경우에만 실행
            user.is_active = False # 활성화 상태만 바꿔줌
            user.save()
            return Response({'msg': f'user_id:{user_pk} deactivated'}, status=status.HTTP_200_OK)
        return Response({'msg': 'you are unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)  
            
        
# 로그인 시 토큰 발급: 확인 완료
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
                
                
                

# 
# class CustomLoginView(LoginView):

#     def login(self):
#         self.user = self.serializer.validated_data['user']
#         access, refresh = jwt_encode(self.user)
#         dit = {
#             'access': access,
#             'refresh': refresh
#         }
#         print('access = ', access)
#         return Response(dit)

            
# Github 로그인용
# class GitHubLogin(SocialLoginView):
#     adapter_class = GitHubOAuth2Adapter
#     callback_url = CALLBACK_URL_YOU_SET_ON_GITHUB
#     client_class = OAuth2Client

