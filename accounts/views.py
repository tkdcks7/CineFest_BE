from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserListserializer,
)
from django.contrib.auth import get_user_model



class UserView(APIView):
    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(get_user_model(), pk=pk)

        else:
            pass

    def post(self, request):
        pass


# class UserViewSet(viewsets.ViewSet):
#     """
#     Example empty viewset demonstrating the standard
#     actions that will be handled by a router class.

#     If you're using format suffixes, make sure to also include
#     the `format=None` keyword argument for each action.
#     """

#     def list(self, request):
#         pass

#     def create(self, request):
#         pass

#     def retrieve(self, request, pk=None):
#         pass

#     def update(self, request, pk=None):
#         pass

#     def partial_update(self, request, pk=None):
#         pass

#     def destroy(self, request, pk=None):
#         pass


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = get_user_model().objects.all()
#     serializer_class = Userserializer


class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer