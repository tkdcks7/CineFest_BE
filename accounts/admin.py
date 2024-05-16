from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group    # admin page에서 사용자 그룹 설정을 위한 모델

from .models import User, Badge


'''
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="비밀번호", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="비밀번호 확인", widget=forms.PasswordInput
    )

    profile_img = forms.ImageField(label="프로필 이미지", required=False)

    class Meta:
        model = User
        fields = ["username", "nickname", "profile_img"]

    # 비밀번호 비교를 위한 password2 확인. cleaned_data를 생성한 후 비교한다. 
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    # 해싱된 비밀번호를 저장
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "nickname",
            "profile_img",
            "is_active",
            "is_admin",
        ]


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["username", "email", "nickname", "is_admin", "is_active"]
    list_filter = ["is_admin"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "username",
                    "nickname",
                    "email",
                    "password",
                    "durgslist",
                    "profile_img",
                ],
            },
        ),
        # ("Personal info", {"fields": ["birthday"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": [
                    "email",
                    "username",
                    "nickname",
                    "profile_img",
                    "durgslist",
                    "password1",
                    "password2",
                ],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
'''