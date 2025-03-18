from django.contrib import admin
from django.urls import path, include
from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)
from djoser.views import TokenCreateView, TokenDestroyView, UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Extend Djoser views with schema descriptions
extended_auth_views = extend_schema_view(
    login=extend_schema(description="User login (returns authentication token)."),
    logout=extend_schema(description="User logout (revokes authentication token)."),
    user_create=extend_schema(description="Register a new user."),
    user_detail=extend_schema(description="Get details of the currently logged-in user."),
)(UserViewSet)

AUTH_PATH = 'auth/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path(AUTH_PATH, include('djoser.urls')),
    path(AUTH_PATH, include('djoser.urls.authtoken')),
    path(AUTH_PATH, include('djoser.urls.jwt')),
    path("auth/jwt/create/", TokenObtainPairView.as_view(), name="jwt-create"),
    path("auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path('accounts/', include('accounts.urls')),
    path('companies/', include('companies.urls')),
    path('tickets/', include('tickets.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
