import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

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
        on_delete=models.CASCADE
    )
    unique_reference = models.CharField(max_length=8, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class TicketHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket.unique_reference} | {self.previous_status} -> {self.new_status}"
