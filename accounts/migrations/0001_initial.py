# Generated by Django 4.2.11 on 2024-05-17 17:15

from django.conf import settings
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='이메일')),
                ('password', models.CharField(max_length=255, verbose_name='비밀번호')),
                ('nickname', models.CharField(max_length=255, verbose_name='닉네임')),
                ('profile_img', models.ImageField(blank=True, null=True, upload_to='profiles/%Y/%m/%d', verbose_name='프로필 이미지')),
                ('point', models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10000000)], verbose_name='유저 포인트')),
                ('tier', models.IntegerField(choices=[(1, 'Iron'), (2, 'Bronze'), (3, 'Silver'), (4, 'Gold'), (5, 'Platinum'), (6, 'Emerald'), (7, 'Diamond'), (8, 'Master'), (9, 'Grandmaster'), (10, 'Challenger')], default=1)),
                ('gender', models.BooleanField(null=True, verbose_name='성별')),
                ('phone_number', models.CharField(max_length=13, null=True, validators=[django.core.validators.RegexValidator('010-?[1-9]\\d{3}-?\\d{4}$')], verbose_name='휴대전화번호')),
                ('is_active', models.BooleanField(default=True, verbose_name='계정활성화 여부')),
                ('is_admin', models.BooleanField(default=False, verbose_name='관리자 여부')),
                ('verified', models.BooleanField(default=False, verbose_name='이메일 인증 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='수정일')),
                ('friends', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='친구')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
