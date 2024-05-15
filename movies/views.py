from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponseNotFound, HttpResponseForbidden

from .serializers import (
    MovieDetailSerializer, 
    MovieListSerializer, 
    CourseDetailSerializer, 
    CourseListSerializer, 
    MenuSerializer,
    CommentSerializer,
    )
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Movie, Genre, Course, Menu, Comment

import requests
import random
from django.conf import settings


# .env에 저장된 환경변수를 settings.py에 불러온 후 이를 다시 가져옴
TMDB_API_TOKEN = settings.TMDB_API_TOKEN
TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = settings.TMDB_BASE_URL

# TMDB에서 장르 id 및 장르 이름을 받아오기 위한 view. db에 삽입 후 주석처리로 비활성화
class GenreView(APIView):
    def get(self, request):
        # TMDB GENRES API에 보낼 requests에 필요한 데이터 작성 
        url = f'{TMDB_BASE_URL}genre/movie/list'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {TMDB_API_TOKEN}'
        }
        payload = { 'language': 'ko' }
        # requests 요청 및 반환값 변환
        response = requests.get(url, headers=headers, params=payload)
        data = response.json()
        genre_lst = data['genres']
        # 반환된 장르 정보를 순회하면서 DB의 Genre table에 저장
        for genre in genre_lst:
            Genre.objects.create(tmdb_id=genre['id'], name=genre['name'])
        return Response({'msg': '장르 목록이 성공적으로 저장됐습니다.'}, status=status.HTTP_201_CREATED)
    
# Sqlite의 Genre table에 저장될 record의 id와, TMDB에서 가져오는 genre의 id를 매칭하는 매직 테이블 선언
# index를 맞추기 위해 매직 테이블의 0번째 index에 없는 id인 0을 삽입
genre_magic_table = [0, 28, 12, 16, 35, 80, 99, 18, 10751, 14, 36, 27, 10402, 9648, 10749, 878, 10770, 53, 10752, 37]
    

class MovieView(APIView):
    @login_required
    def get(self, request, movie_pk=None):
        if movie_pk:
            pass
        else: # 현재 db에 저장된 movielist를 출력
            stored_movies = get_list_or_404(Movie)
            serializer = MovieListSerializer(stored_movies, many=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
    
    @login_required
    def post(self, request):
        pass


class CourseView(APIView):
    @login_required
    def get(self, request, course_pk=None):
        if course_pk:
            course = get_object_or_404(Course, pk=course_pk)
            serializer = CourseDetailSerializer(course)
            return Response(serializer.data)
        else: # ORM을 사용한 filtering을 위해 get_list_or_404 대신 objects.all() 사용
            courses = Course.objects.all() 
            if not courses: # querydict가 빈 값일 시 404 return
                return HttpResponseNotFound("<h1>No Courses</h1>")
            serializer = CourseListSerializer(courses, many=True)
            return Response(serializer.data)
        
    @login_required
    def post(self, request): # 무결성을 위해 course 생성과 동시에 menu도 생성돼야 하므로, menu 생성 로직도 함께 작성한다.
        pass


    @login_required
    def put(self, request, course_pk):
        course = get_object_or_404(Course, pk=course_pk)
        pass


    @login_required
    def delete(self, request, course_pk): # course가 삭제되면 menu 또한 삭제되므로, menu 삭제 로직을 만들 필요가 없음.
        course = get_object_or_404(Course, pk=course_pk)
        if request.user == course.author:
            course.delete()
            return Response({'msg': f'successfully deleted id: {course_pk} course'}, status=status.HTTP_204_NO_CONTENT)
        return HttpResponseForbidden("<h1>You are Not allowed User to Delete This course</h1>")
    

class MenuView(APIView):
    @login_required
    def get(self, request, menu_pk=None):
        if menu_pk:
            menu = get_object_or_404(Menu, pk=menu_pk)
            serializer = MenuSerializer(menu)
            return Response(serializer.data)
        else: # ORM을 사용한 filtering을 위해 get_list_or_404 대신 objects.all() 사용
            menus = Menu.objects.all()
            if not menus: # querydict가 빈 값일 시 404 return
                return HttpResponseNotFound("<h1>No menus</h1>")
            # request.GET에 있는 params에 따른 filtering 작성 필요. 
            serializer = MenuSerializer(menus, many=True)
            return Response(serializer.data)
        

class CommentView(APIView):
    @login_required
    def get(self, request, comment_pk=None):
        if comment_pk:
            comment = get_object_or_404(Menu, pk=comment_pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        else:
            comments = get_list_or_404(Comment)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
    @login_required
    def post(self, request, supcomment_pk=None): # 프론트에서 supcomment pk를 보내주면 pk를 받지 않아도 되려나?
        if supcomment_pk:
            serializer = CommentSerializer(data=request.data, supcomment=get_object_or_404(Comment, pk=supcomment_pk))
        else:
            serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @login_required
    def delete(self, request, comment_pk):
        comment = get_object_or_404(Menu, pk=comment_pk)
        if request.user == comment.author:
            comment.delete()
            return Response({'msg': f'successfully deleted id: {comment_pk} comment'}, status=status.HTTP_204_NO_CONTENT)
        return HttpResponseForbidden('')