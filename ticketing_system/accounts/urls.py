from django.urls import path
from . import views

urlpatterns = [
    # Admin endpoints (list/create users, retrieve/update users)
    path('', views.AdminUserListCreateView.as_view(), name='user-list-create'),
    path('<uuid:pk>/', views.AdminUserRetrieveUpdateView.as_view(), name='user-detail'),
    
    # Regular user endpoint (their own profile)
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
]
