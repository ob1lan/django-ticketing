# tickets/filters.py
import django_filters
from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    """
    Filters for the Ticket model.
    You can filter by priority, status, type, or do partial matches on title.
    """
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Ticket
        fields = {
            'priority': ['exact'],
            'status': ['exact'],
            'type': ['exact'],
        }
