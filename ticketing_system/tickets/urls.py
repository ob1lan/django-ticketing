from django.urls import path
from .views import (
    TicketListCreateView,
    TicketRetrieveUpdateView,
    TicketHistoryListView,
    TicketCommentListCreateView,
    TicketCommentRetrieveUpdateDestroyView,
    TimeSpentListCreateView,
    TimeSpentRetrieveUpdateDestroyView
)

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('<uuid:pk>/', TicketRetrieveUpdateView.as_view(), name='ticket-detail'),
    
    # History
    path('<uuid:pk>/history/', TicketHistoryListView.as_view(), name='ticket-history'),
    
    # Comments
    path('<uuid:pk>/comments/', TicketCommentListCreateView.as_view(), name='ticket-comments-list-create'),
    path('<uuid:pk>/comments/<int:comment_id>/', TicketCommentRetrieveUpdateDestroyView.as_view(), name='ticket-comment-detail'),

    # Time Spent
    path('<uuid:pk>/time-entries/', TimeSpentListCreateView.as_view(), name='time-spent-list-create'),
    path('<uuid:pk>/time-entries/<int:time_id>/', TimeSpentRetrieveUpdateDestroyView.as_view(), name='time-spent-detail'),
]
