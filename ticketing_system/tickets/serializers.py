from rest_framework import serializers
from .models import Ticket, TicketHistory, Comment, TimeSpent


class TicketSerializerLight(serializers.ModelSerializer):
    company_logo = serializers.ReadOnlyField(source='company.logo')
    created_by_fullname = serializers.SerializerMethodField( method_name='get_created_by_fullname')
    def get_created_by_fullname(self, obj):
        return obj.created_by.first_name + ' ' + obj.created_by.last_name
    # If assignee is not set, assignee_fullname will be None
    assignee_fullname = serializers.SerializerMethodField( method_name='get_assignee_fullname')
    def get_assignee_fullname(self, obj):
        if obj.assignee:
            return obj.assignee.first_name + ' ' + obj.assignee.last_name
        return None
    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            # 'description', # Hide description
            'priority',
            'type',
            'status',
            'assignee',
            'assignee_fullname',
            'company',
            'created_by',
            'created_by_fullname',
            'unique_reference',
            'created_at',
            'updated_at',
            'total_time_spent',
            'company_logo',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_by_fullName',
            'unique_reference',
            'created_at',
            'updated_at',
            'assignee_fullname',
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

class TicketSerializer(serializers.ModelSerializer):
    company_logo = serializers.ReadOnlyField(source='company.logo')
    created_by_fullname = serializers.SerializerMethodField( method_name='get_created_by_fullname')
    def get_created_by_fullname(self, obj):
        return obj.created_by.first_name + ' ' + obj.created_by.last_name
    # If assignee is not set, assignee_fullname will be None
    assignee_fullname = serializers.SerializerMethodField( method_name='get_assignee_fullname')
    def get_assignee_fullname(self, obj):
        if obj.assignee:
            return obj.assignee.first_name + ' ' + obj.assignee.last_name
        return None
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
            'assignee_fullname',
            'company',
            'created_by',
            'created_by_fullname',
            'unique_reference',
            'created_at',
            'updated_at',
            'total_time_spent',
            'company_logo',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_by_fullName',
            'unique_reference',
            'created_at',
            'updated_at',
            'assignee_fullname',
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
    user_fullname = serializers.SerializerMethodField( method_name='get_user_fullname')
    def get_user_fullname(self, obj):
        if obj.user:
            return obj.user.first_name + ' ' + obj.user.last_name
    class Meta:
        model = TicketHistory
        fields = [
            'id',
            'event_type',
            'message',
            'previous_status',
            'new_status',
            'changed_at',
            'ticket',
            'user',
            'user_fullname',
        ]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving comments on a ticket.
    """
    author_username = serializers.ReadOnlyField(source='author.email')
    author_role = serializers.ReadOnlyField(source='author.role')
    author_avatar = serializers.ReadOnlyField(source='author.avatar')
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
            'author_avatar',
            'author_role',
            'message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'author', 'author_fullName', 'author_role', 'author_avatar', 'author_username', 'ticket', 'created_at', 'updated_at']


class TimeSpentSerializer(serializers.ModelSerializer):
    operator_name = serializers.ReadOnlyField(source='operator.username')
    operator_fullname = serializers.SerializerMethodField( method_name='get_operator_fullname')
    def get_operator_fullname(self, obj):
        return obj.operator.first_name + ' ' + obj.operator.last_name

    class Meta:
        model = TimeSpent
        fields = [
            'id',
            'ticket',
            'operator',
            'operator_name',
            'operator_fullname',
            'minutes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'ticket', 'operator', 'operator_fullname', 'created_at', 'updated_at']