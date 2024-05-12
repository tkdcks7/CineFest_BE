from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator



class Badage(models.Model):
    class Tierlist(models.IntegerChoices):
        IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND, MASTER, GRANDMASTER, CHALLENGER = list(range(1, 11))
    tier = models.IntegerField(choices=Tierlist)

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
    usertier = models.ForeignKey(Badage, on_delete=models.SET_NULL, null=True,)
    point = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10000000)], default=100)
    email = models.EmailField(unique=True)
    profile_img = models.ImageField(
        upload_to="media/userProfile",
        default="media/userProfile/default.png",
        blank=True,
        null=True,
    )
    # recommend_genre = models.models.ManyToManyField()
    friends = models.ManyToManyField('self', symmetrical=True)

    is_active = models.BooleanField("계정활성화 여부", default=True)
    is_admin = models.BooleanField("관리자 여부", default=False)
    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField("생성일", auto_now_add=True)
    updated_at = models.DateField("수정일", auto_now=True)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["nickname", "username", "password"]

    def __str__(self):
        return (self.email + '   nickname: ' + self.nickname)

    @property
    def is_staff(self):
        return self.is_admin
    

