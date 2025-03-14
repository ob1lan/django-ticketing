from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Ticket, TicketHistory, Comment, TimeSpent
from .serializers import TicketSerializer, TicketHistorySerializer, CommentSerializer, TimeSpentSerializer
from .filters import TicketFilter


@extend_schema(
    description="Retrieve a list of tickets. Staff users see all tickets, while regular users see only tickets related to their company.",
    parameters=[
        OpenApiParameter(name="search", description="Search by title or description", required=False, type=str),
        OpenApiParameter(name="priority", description="Filter by ticket priority", required=False, type=str),
        OpenApiParameter(name="status", description="Filter by ticket status", required=False, type=str),
    ]
)
class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = TicketFilter
    
    # Optional DRF's ?search= queries
    search_fields = ['title', 'description']
    ordering_fields = ['priority', 'status', 'created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Staff can see all tickets
            return Ticket.objects.all()
        else:
            # Non-staff can only see tickets for their own company
            return Ticket.objects.filter(company=user.company)

    def perform_create(self, serializer):
        user = self.request.user
        # Staff: allow picking company from request
        # Non-staff: force to the user's company
        if user.is_staff:
            serializer.save(created_by=user)
        else:
            serializer.save(created_by=user, company=user.company)


@extend_schema(
    description="Retrieve or update a single ticket. Staff users can see all tickets, while regular users see only tickets related to their company."
)
class TicketRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Ticket.objects.all()
        else:
            return Ticket.objects.filter(company=user.company)

    def perform_update(self, serializer):
        user = self.request.user
        ticket_before_update = self.get_object()
        old_status = ticket_before_update.status

        # Same logic: staff can change company, non-staff is forced to use own company
        if user.is_staff:
            updated_ticket = serializer.save()
        else:
            updated_ticket = serializer.save(company=user.company)

        new_status = updated_ticket.status
        if old_status != new_status:
            TicketHistory.objects.create(
                ticket=updated_ticket,
                previous_status=old_status,
                new_status=new_status
            )


@extend_schema(
    description="Retrieve a list of status changes for a given ticket."
)
class TicketHistoryListView(generics.ListAPIView):
    serializer_class = TicketHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ticket_id = self.kwargs['pk']
        if user.is_staff:
            return TicketHistory.objects.filter(ticket__id=ticket_id)
        else:
            return TicketHistory.objects.filter(
                ticket__id=ticket_id,
                ticket__company=user.company
            )


@extend_schema(
    description="Retrieve a list of comments for a given ticket or create a new comment."
)
class TicketCommentListCreateView(generics.ListCreateAPIView):
    """
    - GET: list all comments for a given ticket
    - POST: create a new comment on that ticket
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return comments for the given ticket, applying the same
        company-based visibility logic as TicketListCreateView
        """
        user = self.request.user
        ticket_id = self.kwargs['pk']  # The ticket's UUID from the URL
        if user.is_staff:
            # Staff can see all comments for this ticket
            return Comment.objects.filter(ticket__id=ticket_id)
        else:
            # Non-staff must belong to the ticket's company
            return Comment.objects.filter(
                ticket__id=ticket_id,
                ticket__company=user.company
            )

    def perform_create(self, serializer):
        """
        Ties the new comment to the specified ticket and the request.user.
        """
        ticket_id = self.kwargs['pk']
        user = self.request.user

        # First, get the ticket if user has permission
        try:
            if user.is_staff:
                ticket = Ticket.objects.get(id=ticket_id)
            else:
                ticket = Ticket.objects.get(id=ticket_id, company=user.company)
        except Ticket.DoesNotExist:
            # This will raise a 404 if ticket doesn't exist or user has no access
            raise generics.exceptions.NotFound("Ticket not found or you don't have permission.")

        # Now create the comment
        serializer.save(
            author=user,
            ticket=ticket
        )


@extend_schema(
    description="Retrieve a single comment, update it, or delete it."
)
class TicketCommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
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
        user = self.request.user
        ticket_id = self.kwargs['pk']
        comment_id = self.kwargs['comment_id']
        if user.is_staff:
            return Comment.objects.filter(id=comment_id, ticket__id=ticket_id)
        else:
            return Comment.objects.filter(
                id=comment_id,
                ticket__id=ticket_id,
                ticket__company=user.company
            )

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


@extend_schema(
    description="Retrieve a list of time entries for a given ticket or create a new time entry."
)
class TimeSpentListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeSpentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        ticket_id = self.kwargs['pk']  # the ticket's UUID from URL

        if user.is_staff:
            # staff can see all time entries for the given ticket
            return TimeSpent.objects.filter(ticket__id=ticket_id)
        else:
            # non-staff can only see time entries for tickets belonging to their company
            return TimeSpent.objects.filter(
                ticket__id=ticket_id,
                ticket__company=user.company
            )

    def perform_create(self, serializer):
        # Only staff can create time entries
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can log time.")

        ticket_id = self.kwargs['pk']
        # verify ticket belongs to staff? staff can see all tickets anyway, but let's fetch:
        ticket = Ticket.objects.get(id=ticket_id)
        serializer.save(
            ticket=ticket,
            operator=self.request.user
        )


@extend_schema(
    description="Retrieve a single time entry, update it, or delete it."
)
class TimeSpentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeSpentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    lookup_url_kwarg = 'time_id'
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        ticket_id = self.kwargs['pk']
        time_id = self.kwargs['time_id']

        if user.is_staff:
            return TimeSpent.objects.filter(id=time_id, ticket__id=ticket_id)
        else:
            return TimeSpent.objects.filter(
                id=time_id,
                ticket__id=ticket_id,
                ticket__company=user.company
            )

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can update time entries.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can delete time entries.")
        instance.delete()
