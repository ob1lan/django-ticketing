from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Display in admin list
    list_display = ('id', 'email', 'username', 'phone_number', 'company', 'is_staff', 'is_active')
    # Add filters, search, etc. 
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'company')
