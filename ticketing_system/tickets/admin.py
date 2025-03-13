from django.contrib import admin
from .models import Ticket, TicketHistory

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'unique_reference', 'title', 'company', 'status', 'priority', 'assignee')
    search_fields = ('unique_reference', 'title')
    list_filter = ('status', 'priority', 'company')

@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'previous_status', 'new_status', 'changed_at')
    list_filter = ('changed_at', 'previous_status', 'new_status')
