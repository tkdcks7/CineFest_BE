from rest_framework import serializers
from .models import Genre, Movie, Course, Menu, Comment



class MovieDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('tmdb_id', 'title',)


class CourseDetailSerializer(serializers.ModelSerializer):
    pass


class CourseListSerializer(serializers.ModelSerializer):
    pass


class MenuSerializer(serializers.ModelSerializer):
    pass


class CommentSerializer(serializers.ModelSerializer):
    pass