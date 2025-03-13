from django.urls import path
from .views import (
    TicketListCreateView,
    TicketRetrieveUpdateView,
    TicketHistoryListView
)

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('<uuid:pk>/', TicketRetrieveUpdateView.as_view(), name='ticket-detail'),
    path('<uuid:pk>/history/', TicketHistoryListView.as_view(), name='ticket-history'),
]
