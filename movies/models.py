from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Genre(models.Model):
    tmdb_id = models.IntegerField()
    name = models.CharField(max_length=60)

class Movie(models.Model):
    tmdb_id = models.IntegerField('영화 번호', validators=MinValueValidator(0), unique=True)
    title = models.CharField('영화 제목', max_length=100)
    genres = models.ManyToManyField(Genre, symmetrical=False, related_name='moives')
    overview = models.TextField('영화 개요')
    original_language = models.CharField('출시 국가', max_length=100)
    release_date = models.DateField('개봉일')
    popularity = models.FloatField('인기도', validators=MinValueValidator(0), default=0)
    vote_average = models.FloatField('평점', validators=MinValueValidator(0), default=0)
    post_path = models.CharField(max_length=300)
    post_image = models.ImageField(
        '포스터 이미지',
        upload_to='poster/%Y/%m/%d',
        blank=True,
        null=True,
    )
    is_adult = models.BooleanField('성인영화 여부', default=True)


class Course(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses', verbose_name='코스 작성자')
    title = models.CharField('코스명', max_length=200)
    description = models.TextField('내용')
    vote_total = models.IntegerField('총 투표수', validators=MinValueValidator(0), default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, symmetrical=False, related_name='liked_courses', verbose_name='좋아요')
    reports = models.ManyToManyField(settings.AUTH_USER_MODEL, symmetrical=False, related_name='reported_courses', verbose_name='신고')
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, symmetrical=False, through='Comment')

    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateField('수정일', auto_now=True)


class Menu(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.SET_DEFAULT, default='삭제된 영화입니다.', related_name='menus', verbose_name='영화')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='courses', verbose_name='코스')
    
    class MenuType(models.TextChoices):
        APPETIZER = 'appetizer'
        MAIN = 'main'
        DESSERT = 'dessert'

    type_of_menu = models.CharField('메뉴 종류', choices=MenuType.choices, max_length=10)
    title = models.CharField('메뉴 제목', max_length=200)
    description = models.TextField('감상평')
    

class Comment(models.Model):
    sup_comment = models.ManyToManyField('self', related_name='sub_comments', verbose_name='상위 댓글')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name='작성자')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='코스')
    comment_image = models.ImageField(
        '댓글 이미지',
        upload_to='comment/%Y/%m/%d',
        blank=True,
        null=True,
    )
    content = models.TextField('댓글 내용')
    
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateField('수정일', auto_now=True)