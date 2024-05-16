from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)


class UserListserializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'nickname', 'usertier', 'point',)


class Userserializer(serializers.ModelSerializer):
    friends = UserListserializer(read_only=True, many=True)
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'nickname', 'usertier', 'point',)
        

class UsercreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'nickname', 'usertier', 'point',)
        read_only_fields = ('nickname',)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token