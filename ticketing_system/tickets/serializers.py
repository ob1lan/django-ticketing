from rest_framework import serializers
from .models import Ticket, TicketHistory, Comment, TimeSpent


class TicketSerializer(serializers.ModelSerializer):
    company_logo = serializers.ReadOnlyField(source='company.logo')
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
            'updated_at',
            'total_time_spent',
            'company_logo',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'unique_reference',
            'created_at',
            'updated_at',
            'total_time_spent',
            'company_logo',
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


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving comments on a ticket.
    """
    author_username = serializers.ReadOnlyField(source='author.email')
    author_role = serializers.ReadOnlyField(source='author.role')
    author_fullName = serializers.SerializerMethodField( method_name='get_author_fullName')
    def get_author_fullName(self, obj):
        return obj.author.first_name + ' ' + obj.author.last_name
    

    class Meta:
        model = Comment
        fields = [
            'id',
            'ticket',
            'author',
            'author_username',
            'author_fullName',
            'author_role',
            'message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'author', 'author_fullName', 'author_role', 'author_username', 'ticket', 'created_at', 'updated_at']


class TimeSpentSerializer(serializers.ModelSerializer):
    operator_name = serializers.ReadOnlyField(source='operator.username')

    class Meta:
        model = TimeSpent
        fields = [
            'id',
            'ticket',
            'operator',
            'operator_name',
            'minutes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'ticket', 'operator', 'created_at', 'updated_at']