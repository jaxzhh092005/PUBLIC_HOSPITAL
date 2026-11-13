from django.db import models

from patients.models import Patient

class MedicalFile(models.Model):

    FILE_TYPES = (
        ('PRESCRIPTION','Prescription'),
        ('LAB','Lab Result'),
        ('XRAY','Xray'),
        ('ID','Valid ID'),
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES
    )

    document = models.FileField(
        upload_to='medical_files/'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )