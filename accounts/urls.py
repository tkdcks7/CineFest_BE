from django.urls import path
from . import views


urlpatterns = [
    path('<int:user_pk>/<int:delete_force>/', views.UserView.as_view()),
    path('<int:user_pk>/', views.UserView.as_view()),
    path('', views.UserView.as_view()),
]
