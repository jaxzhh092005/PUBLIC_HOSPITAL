from django.db import models

from patients.models import Patient

from doctors.models import Doctor

class Appointment(models.Model):

    STATUS = (
        ('PENDING','Pending'),
        ('APPROVED','Approved'),
        ('COMPLETED','Completed'),
        ('CANCELLED','Cancelled'),
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='PENDING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )