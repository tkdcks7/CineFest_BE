from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)
from .models import User

from rest_framework import serializers as rest_serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

class UserListserializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'nickname', 'usertier', 'point',)


class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'nickname', 'tier', 'point', 'gender')
        

class UsercreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User(**validated_data)
        password = validated_data.pop('password')
        user.set_password(password)
        user.save()
        return user
    
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'nickname',)


class UserUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = get_user_model()
        fields = ('nickname', 'profile_img', 'gender', 'phone_number',)
        


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        print('customtoken 실행')
        token = super().get_token(user)
        print(token)
        token["email"] = user.email
        print(token)
        return token
    
    
# --------------rest-auth-custom-serializer-----------------

class CustomRegisterSerializer(RegisterSerializer): # 커스텀 후 키 발급 확인
    # email = serializers.EmailField(required=True)
    nickname = rest_serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255
    )
    
    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'nickname': self.validated_data.get('nickname', ''),
        }
    
    
        
        
# class RegisterSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=allauth_account_settings.EMAIL_REQUIRED)
#     password1 = serializers.CharField(write_only=True)
#     password2 = serializers.CharField(write_only=True)

#     def validate_username(self, username):
#         username = get_adapter().clean_username(username)
#         return username