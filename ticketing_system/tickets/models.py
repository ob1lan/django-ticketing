import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings


class Ticket(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    TYPE_CHOICES = (
        ('service_request', 'Service Request'),
        ('change_request', 'Change Request'),
        ('incident', 'Incident'),
    )

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='incident')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tickets'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_tickets'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
    )
    unique_reference = models.CharField(max_length=8, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def total_time_spent(self):
        if not hasattr(self, '_cached_total_time'):
            self._cached_total_time = self.time_entries.aggregate(Sum('minutes'))['minutes__sum'] or 0
        return self._cached_total_time

    def save(self, *args, **kwargs):
        """
        Automatically generate a unique_reference if blank.
        Example format: <COMPANY_INITIALS>-<incremental ID or count>
        """
        if not self.unique_reference and self.company:
            last_count = Ticket.objects.filter(company=self.company).count() + 1
            self.unique_reference = f"{self.company.initials}-{last_count:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unique_reference} - {self.title}"


class Comment(models.Model):
    """
    Represents a comment on a ticket, with an author (User), message,
    and timestamps. Each comment is tied to exactly one Ticket.
    """
    id = models.BigAutoField(primary_key=True)
    ticket = models.ForeignKey(
        Ticket, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment {self.id} by {self.author} on {self.ticket}"


class TicketHistory(models.Model):
    EVENT_CHOICES = [
        ("status_change", "Status Change"),
        ("created", "Created"),
        ("updated", "Updated"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
        ("comment", "Comment Added"),
    ]

    id = models.BigAutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, default='updated')
    message = models.TextField(blank=True, null=True)
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.ticket.unique_reference} | {self.event_type} | {self.changed_at}"


class TimeSpent(models.Model):
    """
    Model to store time spent on a ticket.
    - operator: the staff user who spent the time
    - ticket: reference to the associated Ticket
    - minutes: number of minutes spent
    - created_at, updated_at for auditing
    """
    id = models.BigAutoField(primary_key=True)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    minutes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TimeSpent #{self.id} - {self.minutes} mins on {self.ticket}"