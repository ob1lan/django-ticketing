import uuid
from django.db import models
from django.core.validators import RegexValidator


class Company(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=255)    
    initials = models.CharField(
        max_length=3,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{2,3}$", message="Must be 2-3 uppercase letters")]
    )
    address = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.initials})"
