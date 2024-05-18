from django.urls import path
from . import views

urlpatterns = [
    # path('genre_get/', views.GenreView.as_view()),
    path('', views.MovieView.as_view()),
    path('<int:id>/', views.MovieView.as_view()), # get 요청 시 db에 저장된 movie의 pk, post 요청 시 TMDB API에 사용할 tmdb_id
    path('course/<int:course_pk>/', views.CourseView.as_view()),
    path('course/', views.CourseView.as_view()),
    path('menu/<int:menu_pk>/', views.MenuView.as_view()),
    path('menu/', views.MenuView.as_view()),
    path('search/', views.SearchView.as_view()),
    path('like/<int:course_pk>/', views.LikeView.as_view()),
    path('report/<int:course_pk>/', views.ReportView.as_view()),
    path('ret/', views.RetView.as_view()),
    path('recommend/', views.RecommendView.as_view()),
]
