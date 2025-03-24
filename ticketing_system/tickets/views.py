from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Ticket, TicketHistory, Comment, TimeSpent
from .serializers import (
    TicketSerializer,
    TicketSerializerLight,
    TicketHistorySerializer,
    CommentSerializer,
    TimeSpentSerializer
)
from .filters import TicketFilter
from .mixins import StaffOrCompanyFilterMixin


# ----------------------------------------------------------------------------
#  TICKETS
# ----------------------------------------------------------------------------

@extend_schema(
    description="Retrieve a list of tickets. Staff users see all tickets, while regular users see only tickets related to their company.",
    parameters=[
        OpenApiParameter(name="search", description="Search by title or description", required=False, type=str),
        OpenApiParameter(name="priority", description="Filter by ticket priority", required=False, type=str),
        OpenApiParameter(name="status", description="Filter by ticket status", required=False, type=str),
    ]
)
class TicketListCreateView(StaffOrCompanyFilterMixin, generics.ListCreateAPIView):
    serializer_class = TicketSerializerLight
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = TicketFilter

    # Optional DRF's ?search= queries
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'status', 'created_at', 'updated_at']

    def get_queryset(self):
        queryset = Ticket.objects.all()
        return self.filter_tickets_by_company(queryset)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TicketSerializer
        return TicketSerializerLight


    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            ticket = serializer.save(created_by=user)
        else:
            ticket = serializer.save(created_by=user, company=user.company)

        TicketHistory.objects.create(
            ticket=ticket,
            event_type="created",
            message="Ticket created",
            user=user
        )


@extend_schema(
    description="Retrieve or update a single ticket. Staff users can see all tickets, while regular users see only their company's tickets.",
    responses={
        200: TicketSerializer,
        400: {"description": "Bad request, validation error."},
        403: {"description": "Permission denied."},
        404: {"description": "Ticket not found."}
    }
)
class TicketRetrieveUpdateView(StaffOrCompanyFilterMixin, generics.RetrieveUpdateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.all()
        return self.filter_tickets_by_company(queryset)

    def perform_update(self, serializer):
        user = self.request.user
        ticket = self.get_object()
        old_status = ticket.status

        updated_ticket = serializer.save(company=user.company if not user.is_staff else ticket.company)

        if old_status != updated_ticket.status:
            if updated_ticket.status == "closed":
                TicketHistory.objects.create(
                    ticket=updated_ticket,
                    event_type="closed",
                    previous_status=old_status,
                    new_status=updated_ticket.status,
                    message="Ticket closed",
                    user=user
                )
            elif updated_ticket.status == "resolved":
                TicketHistory.objects.create(
                    ticket=updated_ticket,
                    event_type="resolved",
                    previous_status=old_status,
                    new_status=updated_ticket.status,
                    message="Ticket resolved",
                    user=user
                )
            else:
                TicketHistory.objects.create(
                    ticket=updated_ticket,
                    event_type="status_change",
                    previous_status=old_status,
                    new_status=updated_ticket.status,
                    message="Status changed",
                    user=user
                )
        else:
            # Log a generic update event
            TicketHistory.objects.create(
                ticket=updated_ticket,
                event_type="updated",
                message="Ticket updated",
                user=user
            )


# ----------------------------------------------------------------------------
#  TICKET HISTORY
# ----------------------------------------------------------------------------

@extend_schema(
    description="Retrieve a list of status changes for a given ticket."
)
class TicketHistoryListView(StaffOrCompanyFilterMixin, generics.ListAPIView):
    """
    GET: list all TicketHistory entries for a given ticket.
    Staff sees all, non-staff sees only if ticket.company == user.company.
    """
    serializer_class = TicketHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = TicketHistory.objects.select_related('ticket')
        queryset = self.filter_by_ticket_company(queryset, ticket_id_field='pk')
        return queryset.order_by('-changed_at')
    

class TicketHistoryRetrieveView(StaffOrCompanyFilterMixin, generics.RetrieveAPIView):
    """
    GET: retrieve a single TicketHistory entry.
    Staff sees all, non-staff sees only if ticket.company == user.company.
    """
    serializer_class = TicketHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_url_kwarg = 'history_id'
    lookup_field = 'id'

    def get_queryset(self):
        queryset = TicketHistory.objects.all()
        queryset = self.filter_by_ticket_company(queryset, ticket_id_field='pk')

        history_id = self.kwargs['history_id']
        return queryset.filter(id=history_id)


# ----------------------------------------------------------------------------
#  COMMENTS
# ----------------------------------------------------------------------------

@extend_schema(
    description="Retrieve a list of comments for a given ticket or create a new comment."
)
class TicketCommentListCreateView(StaffOrCompanyFilterMixin, generics.ListCreateAPIView):
    """
    - GET: list all comments for a given ticket
    - POST: create a new comment on that ticket
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Comment.objects.select_related('ticket', 'author')
        queryset = self.filter_by_ticket_company(queryset, ticket_id_field='pk')
        return queryset.order_by('created_at')

    def perform_create(self, serializer):
        """
        Ties the new comment to the specified ticket and the request.user.
        """
        user = self.request.user
        ticket_id = self.kwargs['pk']

        # Check the ticket exists and belongs to user.company (unless staff)
        try:
            if user.is_staff:
                ticket = Ticket.objects.get(id=ticket_id)
            else:
                ticket = Ticket.objects.get(id=ticket_id, company=user.company)
        except Ticket.DoesNotExist:
            raise generics.exceptions.NotFound("Ticket not found or you don't have permission.")

        # Now create the comment
        serializer.save(author=user, ticket=ticket)
        
        TicketHistory.objects.create(
            ticket=ticket,
            event_type="comment",
            message=f"{user.get_full_name() or user.email} commented on the ticket."
        )


@extend_schema(
    description="Retrieve a single comment, update it, or delete it."
)
class TicketCommentRetrieveUpdateDestroyView(StaffOrCompanyFilterMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    - GET a single comment
    - PUT/PATCH to edit it (maybe only staff or the original author)
    - DELETE to remove it
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_url_kwarg = 'comment_id'
    lookup_field = 'id'

    def get_queryset(self):
        queryset = Comment.objects.all()
        # Filter by the ticket's UUID (pk) using the mixin
        queryset = self.filter_by_ticket_company(queryset, ticket_id_field='pk')

        # Also filter by the specific comment ID
        comment_id = self.kwargs['comment_id']
        return queryset.filter(id=comment_id)

    def perform_update(self, serializer):
        # Optionally enforce that only the 'author' or staff can edit
        if not self.request.user.is_staff:
            comment = self.get_object()
            if comment.author != self.request.user:
                raise generics.exceptions.PermissionDenied("You cannot edit someone else's comment.")
        serializer.save()

    def perform_destroy(self, instance):
        # Same check if you want
        if not self.request.user.is_staff:
            if instance.author != self.request.user:
                raise generics.exceptions.PermissionDenied("You cannot delete someone else's comment.")
        instance.delete()


# ----------------------------------------------------------------------------
#  TIME SPENT
# ----------------------------------------------------------------------------

@extend_schema(
    description="Retrieve a list of time entries for a given ticket or create a new time entry."
)
class TimeSpentListCreateView(StaffOrCompanyFilterMixin, generics.ListCreateAPIView):
    serializer_class = TimeSpentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = TimeSpent.objects.select_related('ticket', 'operator')
        queryset = self.filter_by_ticket_company(queryset, ticket_id_field='pk')
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Only staff can create time entries
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can log time.")

        ticket_id = self.kwargs['pk']
        ticket = Ticket.objects.get(id=ticket_id)  # staff can see all tickets
        serializer.save(ticket=ticket, operator=self.request.user)


@extend_schema(
    description="Retrieve a single time entry, update it, or delete it."
)
class TimeSpentRetrieveUpdateDestroyView(StaffOrCompanyFilterMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeSpentSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_url_kwarg = 'time_id'
    lookup_field = 'id'

    def get_queryset(self):
        queryset = TimeSpent.objects.all()
        # Filter by the ticket's UUID (pk) using the mixin
        queryset = self.filter_by_ticket_company(queryset, ticket_id_field='pk')

        # Also filter by the specific time entry ID
        time_id = self.kwargs['time_id']
        return queryset.filter(id=time_id)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can update time entries.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can delete time entries.")
        instance.delete()
