from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile

from .serializers import (
    MovieDetailSerializer, 
    MovieListSerializer, 
    CourseDetailSerializer, 
    CourseListSerializer, 
    CourseCreateSerializer,
    MenuSerializer,
    CommentSerializer,
    SearchSerializer,
    )
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Movie, Genre, Course, Menu, Comment

import requests
import random
import json
from io import BytesIO
import base64
from datetime import datetime
from PIL import Image
from django.conf import settings


# .env에 저장된 환경변수를 settings.py에 불러온 후 이를 다시 가져옴
TMDB_API_TOKEN = settings.TMDB_API_TOKEN
TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = settings.TMDB_BASE_URL
TMDB_IMG_URL = settings.TMDB_IMG_URL
OPENWEATHER_LOCATION_URL = settings.OPENWEATHER_LOCATION_URL
OPENWEATHER_WEATHER_URL = settings.OPENWEATHER_WEATHER_URL
OPENWEATHER_API_KEY = settings.OPENWEATHER_API_KEY

# TMDB에서 장르 id 및 장르 이름을 받아오기 위한 view. db에 삽입 후 주석처리로 비활성화. 작동 확인
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
        print(data)
        genre_lst = data['genres']
        # 반환된 장르 정보를 순회하면서 DB의 Genre table에 저장
        for genre in genre_lst:
            Genre.objects.create(tmdb_id=genre['id'], name=genre['name'])
        return Response({'msg': '장르 목록이 성공적으로 저장됐습니다.'}, status=status.HTTP_201_CREATED)
    
# Sqlite의 Genre table에 저장될 record의 id와, TMDB에서 가져오는 genre의 id를 매칭하는 매직 테이블 선언
# index를 맞추기 위해 매직 테이블의 0번째 index에 없는 id인 0을 삽입
genre_magic_table = [0, 28, 12, 16, 35, 80, 99, 18, 10751, 14, 36, 27, 10402, 9648, 10749, 878, 10770, 53, 10752, 37]
genre_name_table = ['', '액션', '모험', '애니메이션', '코미디', '범죄', '다큐멘터리', '드라마', '가족', 
                    '판타지', '역사', '공포', '음악', '미스터리', '로맨스', 'SF', 'TV 영화', '스릴러', '전쟁', '서부']
    

class MovieView(APIView):
    # @login_required
    def get(self, request, id=None):
        if id:
            movie = get_object_or_404(Movie, pk=id)
            serializer = MovieDetailSerializer(movie)
            return Response(serializer.data)
        else: # 현재 db에 저장된 movielist를 출력. 요청 유저의 선호 장르를 상단으로. 이외의 장르는 
            stored_movies = Movie.objects.all()
            serializer = MovieListSerializer(stored_movies, many=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)

    # @login_required
    def post(self, request, id): # TMDB에서 list로 들고올 때와 detail로 들고올 때 약간 다른 형식의 keyname, value 존재
        url = f'{TMDB_BASE_URL}movie/{id}'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {TMDB_API_TOKEN}'
        }
        payload = { 'language': 'ko-KR' } # 한국으로 설정됐는데 overview가 없을 경우에 관한 경우를 추가?
        # requests 요청 및 반환값 변환
        response = requests.get(url, headers=headers, params=payload)
        data = response.json()
        genres = data.pop('genres')
        backdrop_path = data.get('backdrop_path')
        if backdrop_path:
            img_data = requests.get(TMDB_IMG_URL + backdrop_path)
            image_files = ContentFile(img_data.content, name=f'{data.get('title') + '_poster.jpeg'}')
            data['post_image'] = image_files
        # genres의 value를 dict 에서 integer로. id만 추출하여 알맞은 형식으로 변형
        serializer = MovieDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            movie = serializer.save(tmdb_id=id)
            for genre in genres: # 생성된 Movie instance와 Genre간 M:M relation을 만든다. 
                movie.genres.add(get_object_or_404(Genre, tmdb_id=genre['id']))
            # 이미지 저장 로직
            return Response(serializer.data, status=status.HTTP_201_CREATED)



class CourseView(APIView):
    # @login_required
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
        
    # @login_required
    def post(self, request): # 무결성을 위해 course 생성과 동시에 menu도 생성돼야 하므로, menu 생성 로직도 함께 작성한다.
        course_data = request.data
        appetizer_data = course_data.get('appetizer')
        main_data = course_data.get('main')
        dessert_data = course_data.get('dessert')
        if (
            appetizer_data.get('movie') == main_data.get('movie')
            or appetizer_data.get('movie') == dessert_data.get('movie')
            or main_data.get('movie') == dessert_data.get('movie')
        ):
            return Response({'msg': 'Menu는 모두 다른 영화여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        course_info_serializer = CourseCreateSerializer(data=course_data)
        appetizer_serializer = MenuSerializer(data=appetizer_data)
        main_serializer = MenuSerializer(data=main_data)
        dessert_serializer = MenuSerializer(data=dessert_data)
        if (
            course_info_serializer.is_valid(raise_exception=True)
            and appetizer_serializer.is_valid(raise_exception=True)
            and main_serializer.is_valid(raise_exception=True)
            and dessert_serializer.is_valid(raise_exception=True)
        ):
            course = course_info_serializer.save(author=request.user)
            appetizer_serializer.save(course=course)
            main_serializer.save(course=course)
            dessert_serializer.save(course=course)
            request.user.point += 10
            return Response(course_info_serializer.data, status=status.HTTP_201_CREATED)
        
    @login_required
    def put(self, request, course_pk):
        course = get_object_or_404(Course, pk=course_pk)
        pass


    @login_required
    def delete(self, request, course_pk): # course가 삭제되면 menu 또한 삭제되므로, menu 삭제 로직을 만들 필요가 없음.
        course = get_object_or_404(Course, pk=course_pk)
        if request.user == course.author and not course.is_reported: # 요청자와 작성자가 일치하고, 신고되지 않은 경우에만 삭제 가능
            course.delete()
            request.user.point -= 10
            return Response({'msg': f'successfully deleted id: {course_pk} course'}, status=status.HTTP_204_NO_CONTENT)
        return HttpResponseForbidden("<h1>You are Not allowed User to Delete This course</h1>")
    

# Menu post: Course 작성 시 생성되므로 없음.
# Menu delete: Course 삭제 시 on_delete CASCADE라 같이 삭제되므로 없음.
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
        

# 댓글 수정은 기본적으로 지원하지 않을 계획
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
    def post(self, request, course_pk, supcomment_pk=None): # 프론트에서 supcomment pk를 보내주면 pk를 받지 않아도 되려나?
        if supcomment_pk:
            course = get_object_or_404(Course, pk=course_pk)
            supcomment = Comment.objects.get(pk=supcomment_pk) # supcomment_pk가 주어지지 않으면 supcomment = None이므로 null로 저장됨
            serializer = CommentSerializer(data=request.data)
        else:
            serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(course=course, author=request.user, supcomment=supcomment)
            request.user.point += 1 # 댓글 작성 시 point 1 증가
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @login_required
    def delete(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        if request.user == comment.author or request.user == comment.course.author: # 댓글 작성자 혹은 댓글이 달린 course의 작성자만 삭제 가능
            comment.author.point -= 2 # 댓글 삭제 시 point 2 감소
            comment.delete()
            return Response({'msg': f'successfully deleted id: {comment_pk} comment'}, status=status.HTTP_204_NO_CONTENT)
        return HttpResponseForbidden('')
    

# SearchView 작동 확인. 
# null 처리를 위해 serializer poster_path에 allow_null=True 설정
class SearchView(APIView):
    # @login_required
    def get(self, request):
        # Front에서 받은 request를 
        queries = request.GET
        query = queries.get('query')
        include_adult = queries.get('include_adult')
        language = queries.get('language')
        primary_release_year = queries.get('primary_release_year')
        page = queries.get('page')
        region = queries.get('region')
        year = queries.get('year')
        
        url = f'{TMDB_BASE_URL}search/movie'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {TMDB_API_TOKEN}'
        }
        payload = { 
                   'query': query,
                   'include_adult': include_adult,
                   'language': language,
                   'primary_release_year': primary_release_year,
                   'page': page,
                   'region': region,
                   'year': year,
                   }
        # TMDB 검색 API에 요청 및 반환값 변환
        response = requests.get(url, headers=headers, params=payload)
        data = response.json()
        movies_info_list = data.get('results')
        serializer = SearchSerializer(data=movies_info_list, many=True)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)
            

# 좋아요 기능. Course instance-request user 간 관계가 있으면 삭제, 없으면 생성 후 is_liked를 반환
class LikeView(APIView):
    # @login_required
    def post(self, request, course_pk):
        course = get_object_or_404(Course, pk=course_pk)
        user = request.user
        is_liked = course.likes.filter(pk=user.pk).exists()
        if is_liked:
            course.likes.remove(user)
        else:
            course.likes.add(user)
        return Response({'msg': f'{ "canceled like" if is_liked else "like"}', 'is_liked': not is_liked}, status=status.HTTP_200_OK)
    

# 신고 기능. PLATINUM 이상 유저만 신고 가능. 신고 카운트가 10 되면 해당 Course 신고처리 후 Course 작성자가 보유한 포인트 50 삭감.
class ReportView(APIView):
    # @login_required
    def post(self, request, course_pk):
        user = request.user
        if request.user.tier < 5:
            return Response({'msg': 'you have to rank up to use report system.'}, status=status.HTTP_401_UNAUTHORIZED)
        course = get_object_or_404(Course, pk=course_pk)
        if course.is_reported:
            return Response({'msg': 'this Course is already has been reported.'}, status=status.HTTP_400_BAD_REQUEST)
        if course.reports.filter(pk=user.pk).exists():
            return Response({'msg': 'you\'ve been already reported this Course.'}, status=status.HTTP_400_BAD_REQUEST)
        if course.reports.count() == 9:
            course.is_reported = True
            course.author.point -= 50
        course.reports.add(user)
        return Response({'msg': 'Thank you for your attribution for our restaurant.'}, status=status.HTTP_200_OK)
    

# 영화 추천 알고리즘
class RecommendView(APIView):
    def get(self, request):
        recommend_methods = request.GET.get('recommend_methods')
        # recommend_methods에 담긴 데이터가 JSON이라면 아래 주석을 활성화하여 dict으로 변환
        # recommend_methods = json.loads(recommend_methods)

        # method 종류는 date, time, weather, gender, selet_genre 등이 있을듯?
        if recommend_methods.get('mychoices'): # 본인 설정한 장르에 따른 추천
            genres_choiced = recommend_methods['mychoices']
            recommend_movies = Movie.objects.filter(genres__name__in=genres_choiced)[:16]
            serializer = MovieListSerializer(recommend_movies, many=True)
            return Response(serializer.data)
        else: # 본인이 선택한 장르에 따른 영화 추천
            # OpenWeather API로, 도시 이름을 입력받아 사용자 거주 지역의 위도-경도 산출
            # 위도-경도값을 입력받아, 현재 날씨를 추출
            # 현재 날씨를 바탕으로 추천 영화 filtering
            recommend_genres = {'액션', '모험', '애니메이션', '코미디', '범죄', '다큐멘터리', '드라마', '가족', 
                        '판타지', '역사', '공포', '음악', '미스터리', '로맨스', 'SF', 'TV 영화', '스릴러', '전쟁', '서부'}
            if recommend_methods.get('weather'): # weather 추천 활성화.
                # Openweather API를 이용해, 도시 이름을 바탕으로 위치인 latitude(위도), longitude(경도)를 반환하는 로직 작성
                city = recommend_methods['weather']['city']
                response_location = requests.get(OPENWEATHER_LOCATION_URL, params={'appid': OPENWEATHER_API_KEY, 'q': city})
                data_location = response_location.json()
                lat = data_location.get('lat')
                lon = data_location.get('lon')
                # Openweather API를 이용해, lat, lon을 바탕으로 현재 날씨를 받아옴.
                payload = {
                    'appid': OPENWEATHER_API_KEY,
                    'lat': lat,
                    'lon': lon,
                    'units': 'metric'
                }
                response_weather = requests.get(OPENWEATHER_WEATHER_URL, params=payload)
                data_weather = response_weather.json()
                weather_id = data_weather.get('weather').get('id')
                weather_filter_dict = {
                    2: ['코미디', '음악', '로맨스', 'TV 영화', '서부'],
                    3: ['액션', '범죄', '스릴러', '역사', '공포', '서부'],
                    5: ['코미디', '음악', '로맨스', 'TV 영화', '서부'],
                    6: ['다큐멘터리', '스릴러', '역사', '미스터리', '공포', '서부'],
                    7: ['범죄', '다큐멘터리', '스릴러', '역사', '미스터리', '전쟁', '공포'],
                    8: ['범죄', '스릴러', '역사', '미스터리', '공포'],
                    9: ['음악', '로맨스', 'TV 영화', '서부'],
                }
                # 날씨별 세 자리 id를 추출해 1자리의 숫자로 만듦. https://openweathermap.org/weather-conditions 참고.
                if weather_id > 802: # 800: 맑음, 803, 804: 구름 많음이라 803, 804에 대한 처리
                    weather_id = 900
                weather_id //= 100
                # 날씨 필터링에 대응되는 장르는 추천 장르에서 제거
                recommend_genres = recommend_genres - set(weather_filter_dict.get(weather_id)) 

            # 시간대에 따른 filtering
            if recommend_methods['times']:
                now = datetime.now()
                weekday = now.weekday()
                hour = now.hour
                # 6~17, 18~23, 23~익일 5시로 구분
                if weekday < 5: # 평일인 경우
                    if 6 <= hour < 18:
                        hour_filters = {'액션', '모험', '가족', '로맨스', 'TV영화', '공포'}
                    elif 18 <= hour < 23:
                        hour_filters = {'다큐멘터리', '범죄', '드라마', '역사', '공포'}
                    else:
                        hour_filters = {'음악', '로맨스', 'TV 영화'}
                    recommend_genres = recommend_genres - hour_filters
            # 필터링된 추천 장르를 바탕으로 영화 쿼리셋 가져오기
            recommend_movies = Movie.objects.filter(genres__name__in=recommend_genres)[:16]
        
# DALL-E를 이용한 Course에 있는 영화 3편을 섞은 이미지 생성? 
# Chat-GPT를 이용한 영화 추천?

# Genre table에 있는 record들의 name을 출력하고 response로 보내는 View
class RetView(APIView):
    def get(self, request):
        # genres = Genre.objects.all()
        # lst = []
        # for gen in genres:
        #     lst.append(gen.name)
        # print(lst)
        imgurl = 'https://image.tmdb.org/t/p/w500/f5MtI3ZWoCdquEHOdkldlCuHs6t.jpg'
        data = requests.get(url=imgurl).content
        print(data)
        f = open('img.jpg', 'wb')
        f.write(data)
        f.close()
        img = Image.open('img.jpg')
        img.show()
        # image_res = Image.open(BytesIO(data.content))
        return Response({'img':1})