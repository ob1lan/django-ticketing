from django.contrib import admin
from django.urls import path, include
from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)
from djoser.views import TokenCreateView, TokenDestroyView, UserViewSet

# Extend Djoser views with schema descriptions
extended_auth_views = extend_schema_view(
    login=extend_schema(description="User login (returns authentication token)."),
    logout=extend_schema(description="User logout (revokes authentication token)."),
    user_create=extend_schema(description="Register a new user."),
    user_detail=extend_schema(description="Get details of the currently logged-in user."),
)(UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # DRF login/logout
    path('auth/', include('djoser.urls')),  # Djoser authentication
    path('auth/', include('djoser.urls.authtoken')),  # Token authentication endpoints
    path('accounts/', include('accounts.urls')),
    path('companies/', include('companies.urls')),
    path('tickets/', include('tickets.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
