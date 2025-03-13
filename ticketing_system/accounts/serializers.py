from rest_framework import serializers
from .models import User

class AdminUserSerializer(serializers.ModelSerializer):
    """
    For staff/admin usage. They can create users, set passwords, assign companies, etc.
    """
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username',
            'first_name', 'last_name', 'phone_number',
            'company',  # admin can select any company for a user
            'is_staff', 'is_active', 'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            # Optionally set a default password if none is provided
            user.set_password('changeme123')
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    For a regular user to view/update their own data,
    but can't change email/company (depending on your rules).
    """
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'company',
        ]
        read_only_fields = ['email', 'company']
