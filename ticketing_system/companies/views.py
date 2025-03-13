from rest_framework import generics, permissions
from .models import Company
from .serializers import CompanySerializer

class CompanyListCreateView(generics.ListCreateAPIView):
    """
    Allows listing all companies (GET) or creating (POST).
    Typically, only staff or superuser might create new companies.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

class CompanyRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Allows retrieving/updating a single Company instance.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
