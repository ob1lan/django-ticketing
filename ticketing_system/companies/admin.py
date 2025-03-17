from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'initials', 'contact_phone', 'logo')
    search_fields = ('name', 'initials')
