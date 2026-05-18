"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from apps.decks.urls import deck_router
from apps.users.views import CustomTokenObtainPairView, RegisterView
from apps.words.urls import router

RefreshView = extend_schema(summary="Refresh access token")(TokenRefreshView)

BlacklistView = extend_schema(summary="Logout dan blacklist refresh token")(
    TokenBlacklistView
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", CustomTokenObtainPairView.as_view()),
    path("api/auth/token/refresh/", RefreshView.as_view()),
    path("api/auth/logout/", BlacklistView.as_view()),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/", include(router.urls)),
    path("api/", include(deck_router.urls)),
    path("api/", include("apps.flashcards.urls")),
]
