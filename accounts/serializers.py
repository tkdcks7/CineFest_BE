from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenObtainSerializer,
)


class UserListserializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        feilds = ('email', 'nickname', 'usertier', 'point',)


class Userserializer(serializers.ModelSerializer):
    class UserFriendNameSerializer(serializers.ModelSerializer):
        pass
    class Meta:
        model = get_user_model()
        feilds = ('email', 'nickname', 'usertier', 'point',)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token