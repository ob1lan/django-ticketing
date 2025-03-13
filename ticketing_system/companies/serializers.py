from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for basic Company info.
    """
    class Meta:
        model = Company
        fields = '__all__'
