from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("DOCTOR", "Doctor"),
        ("PATIENT", "Patient"),
        ("NURSE", "Nurse"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class Profile(models.Model):
    """Extra account details. First name, last name and email stay on the Django user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    middle_name = models.CharField(max_length=60, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True, help_text="Stored as +639XXXXXXXXX")

    def __str__(self):
        return f"Profile of {self.user}"