from rest_framework import generics, permissions
from .models import Ticket, TicketHistory
from .serializers import TicketSerializer, TicketHistorySerializer

class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

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
