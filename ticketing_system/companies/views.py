from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from .models import Company
from .serializers import CompanySerializer


@extend_schema(
    description="Retrieve a list of companies or create a new company."
)
class CompanyListCreateView(generics.ListCreateAPIView):
    """
    Allows listing all companies (GET) or creating (POST).
    Typically, only staff or superuser might create new companies.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    description="Retrieve or update a single company."
)
class CompanyRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    Allows retrieving/updating a single Company instance.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
