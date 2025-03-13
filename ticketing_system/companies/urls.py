from django.urls import path
from .views import CompanyListCreateView, CompanyRetrieveUpdateView

urlpatterns = [
    path('', CompanyListCreateView.as_view(), name='company-list-create'),
    path('<uuid:pk>/', CompanyRetrieveUpdateView.as_view(), name='company-detail'),
]
