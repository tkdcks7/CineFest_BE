from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from django.conf import settings
from django.conf.urls import static
from django.conf.urls.static import static

from accounts.views import Login
# from accounts.views import GitHubLogin # Github 로그인용

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/movies/', include('movies.urls')),
    path('api/token/', Login.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    # path('dj-rest-auth/github/', GitHubLogin.as_view(), name='github_login')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
