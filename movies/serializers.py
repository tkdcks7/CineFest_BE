from rest_framework import serializers
from .models import Genre, Movie, Course, Menu, Comment



class MovieDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ('tmdb_id',)


class MovieListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        fields = ('tmdb_id', 'title',)


class CourseDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Course
        fields = '__all__'


class CourseCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Course
        fields = ('author', 'title', 'description',)
        read_only_fields = ('author',)


class CourseListSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count',)
    
    class Meta:
        model = Course
        fields = ('id', 'author', 'title',)


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('course', 'author',)


class SearchSerializer(serializers.Serializer):
    adult = serializers.BooleanField()
    backdrop_path = serializers.CharField(allow_null=True)
    genre_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
    id = serializers.IntegerField()
    original_language = serializers.CharField()
    original_title = serializers.CharField()
    overview = serializers.CharField()
    popularity = serializers.FloatField()
    poster_path = serializers.CharField(allow_null=True)
    release_date = serializers.DateField()
    title = serializers.CharField()
    video = serializers.BooleanField()
    vote_average = serializers.FloatField()
    vote_count = serializers.IntegerField()
