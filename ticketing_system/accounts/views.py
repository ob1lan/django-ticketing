from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import (
    AdminUserSerializer,
    UserProfileSerializer
)


@extend_schema(
    description="Allows staff (is_staff=True) to list all users and create new ones."
)
class AdminUserListCreateView(generics.ListCreateAPIView):
    """
    Allows staff (is_staff=True) to list all users and create new ones.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    # Only staff users can access
    permission_classes = [permissions.IsAdminUser]


@extend_schema(
    description="Allows staff to retrieve or update a specific user by ID."
)
class AdminUserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Allows staff to retrieve or update a specific user by ID.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(
    description="Retrieves and updates the currently logged-in user's profile."
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieves and updates the currently logged-in user's profile.
    - GET /accounts/profile/ -> retrieve user info
    - PUT/PATCH /accounts/profile/ -> update user info
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
