from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),         # DRF login/logout
    path('auth/', include('djoser.urls')),                     # Djoser base endpoints
    path('auth/', include('djoser.urls.authtoken')),           # Token auth endpoints
    path('accounts/', include('accounts.urls')),               # We'll define soon
    path('companies/', include('companies.urls')),             # We'll define soon
    path('tickets/', include('tickets.urls')),                 # We'll define soon
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
