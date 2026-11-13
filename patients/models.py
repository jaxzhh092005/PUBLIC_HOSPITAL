from django.db import models
from accounts.models import User

class Patient(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    birthdate = models.DateField()

    gender = models.CharField(max_length=20)

    mobile = models.CharField(max_length=20)

    address = models.TextField()

    emergency_contact = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username