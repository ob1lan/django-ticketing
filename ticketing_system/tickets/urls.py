from django.urls import path
from .views import (
    TicketListCreateView,
    TicketRetrieveUpdateView,
    TicketHistoryListView,
    TicketCommentListCreateView,
    TicketCommentRetrieveUpdateDestroyView
)

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('<uuid:pk>/', TicketRetrieveUpdateView.as_view(), name='ticket-detail'),
    path('<uuid:pk>/history/', TicketHistoryListView.as_view(), name='ticket-history'),
    path('<uuid:pk>/comments/', TicketCommentListCreateView.as_view(), name='ticket-comments-list-create'),
    path('<uuid:pk>/comments/<int:comment_id>/', TicketCommentRetrieveUpdateDestroyView.as_view(),
         name='ticket-comment-detail'),
]
