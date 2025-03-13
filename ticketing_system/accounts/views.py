from rest_framework import generics, permissions
from .models import User
from .serializers import (
    AdminUserSerializer,
    UserProfileSerializer
)


class AdminUserListCreateView(generics.ListCreateAPIView):
    """
    Allows staff (is_staff=True) to list all users and create new ones.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    # Only staff users can access
    permission_classes = [permissions.IsAdminUser]


class AdminUserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Allows staff to retrieve or update a specific user by ID.
    """
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


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
