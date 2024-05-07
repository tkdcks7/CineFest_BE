from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, nickname, email, password=None):
        if not email:
            raise ValueError("이메일은 필수입니다.")

        user = self.model(
            username=username,
            nickname=nickname,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, email, password):
        user = self.create_user(
            username=username,
            nickname=nickname,
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField("아이디", max_length=30, unique=True)
    password = models.CharField("비밀번호", max_length=255)
    nickname = models.CharField(max_length=30, unique=False)
    email = models.EmailField(unique=True)
    profile_img = models.ImageField(
        upload_to="media/userProfile",
        default="media/userProfile/default.png",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField("관리자 여부", default=False)
    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField("수정일", auto_now=True)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname", "username", "password"]

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin