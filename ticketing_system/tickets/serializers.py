# tickets/serializers.py
from rest_framework import serializers
from .models import Ticket, TicketHistory

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            'description',
            'priority',
            'type',
            'status',
            'assignee',
            'company',
            'created_by',
            'unique_reference',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_by',
            'unique_reference',
            'created_at',
            'updated_at',
        ]

    def get_fields(self):
        """
        Hide the 'company' field from non-staff users so they don't even see it in
        the browsable API or have the option to supply it.
        """
        fields = super().get_fields()
        request = self.context.get('request')

        if request and not request.user.is_staff:
            fields.pop('company', None)

        return fields

class TicketHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketHistory
        fields = '__all__'
