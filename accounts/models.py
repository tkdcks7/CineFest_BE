from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from allauth.account.adapter import DefaultAccountAdapter

class UserManager(BaseUserManager):
    def create_user(self, nickname, email, password=None):
        if not email:
            raise ValueError("이메일은 필수입니다.")

        user = self.model(
            nickname=nickname,
            email=self.normalize_email(email),
        )
        if not password:
            raise ValueError("password는 필수입니다.")
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nickname):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            nickname=nickname,
        )
        user.is_admin = True
        user.is_active = True
        user.is_verified = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    # username = models.CharField('유저네임인데 안 씀', unique=False, default='None', max_length=5)
    email = models.EmailField('이메일', unique=True)
    password = models.CharField('비밀번호', max_length=255)
    nickname = models.CharField('닉네임', max_length=255, unique=False)
    profile_img = models.ImageField(
        '프로필 이미지',
        upload_to="profiles/%Y/%m/%d",
        blank=True,
        null=True,
    )

    point = models.IntegerField('유저 포인트', validators=[MinValueValidator(0), MaxValueValidator(10000000)], default=100)
    class Tierlist(models.IntegerChoices):
        IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND, MASTER, GRANDMASTER, CHALLENGER = tuple(range(1, 11))
    tier = models.IntegerField(choices=Tierlist.choices, default=1)
    
    recommend_genre = models.ManyToManyField('movies.Genre', symmetrical=False, verbose_name='genre_like_users')
    gender = models.BooleanField('성별', null=True)
    # 대한민국 휴대전화번호 Regex
    phone_number = models.CharField('휴대전화번호', validators=[RegexValidator(r'010-?[1-9]\d{3}-?\d{4}$')], max_length=13, null=True)
    friends = models.ManyToManyField('self', symmetrical=True, verbose_name='친구')

    is_active = models.BooleanField('계정활성화 여부', default=True)
    is_admin = models.BooleanField('관리자 여부', default=False)
    verified = models.BooleanField('이메일 인증 여부', default=False)

    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateField('수정일', auto_now=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return (self.email + '   nickname: ' + self.nickname)

    @property
    def is_staff(self):
        return self.is_admin


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_email, user_field # user_username
        data = form.cleaned_data
        email = data.get("email")
        # username = data.get("username")
        # nickname 필드를 추가
        nickname = data.get("nickname")
        user_email(user, email)
        # user_username(user, username)
        if nickname:
            user_field(user, "nickname", nickname)
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        # self.populate_username(request, user)
        if commit:
        # Ability not to commit makes it easier to derive from
        # this adapter by adding
            user.save()
        return user

