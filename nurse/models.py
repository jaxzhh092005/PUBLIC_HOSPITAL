from django.db import models

from accounts.models import User
from hospitals.models import Hospital
from patients.models import Patient


class Nurse(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE
    )

class VitalSign(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    blood_pressure = models.CharField(
        max_length=20
    )

    pulse_rate = models.IntegerField()

    oxygen = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )