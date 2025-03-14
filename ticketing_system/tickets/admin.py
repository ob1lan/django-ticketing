from django.contrib import admin
from .models import Ticket, TicketHistory, Comment, TimeSpent


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'unique_reference', 'title', 'company', 'status', 'priority', 'assignee')
    search_fields = ('unique_reference', 'title')
    list_filter = ('status', 'priority', 'company')


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'previous_status', 'new_status', 'changed_at')
    list_filter = ('changed_at', 'previous_status', 'new_status')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'author', 'created_at', 'updated_at')
    search_fields = ('message', 'author__email', 'author__username')
    list_filter = ('created_at', 'author')


@admin.register(TimeSpent)
class TimeSpentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'operator', 'minutes', 'created_at')
    search_fields = ('operator__username', 'ticket__title')
    list_filter = ('operator', 'ticket')