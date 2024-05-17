from django.contrib import admin
from .models import Genre, Movie, Course, Menu, Comment


admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Course)
admin.site.register(Menu)
admin.site.register(Comment)