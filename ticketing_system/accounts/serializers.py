from rest_framework import serializers
from .models import User
from companies.models import Company
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
            'company', 'avatar',
            'is_staff', 'is_active', 'role', 'password',
        ]
        
    def validate_company(self, value):
        if value is None:
            return value
        if not Company.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Company does not exist.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            raise KeyError("Password is required.")
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
            'avatar',
        ]
        read_only_fields = ['company', 'username']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        # Assuming you have a 'role' field or a method to get the user's role:
        token['role'] = user.role if hasattr(user, 'role') else 'user'
        return token