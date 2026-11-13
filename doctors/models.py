from django.db import models
from accounts.models import User
from hospitals.models import Hospital


class Doctor(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE
    )

    specialization = models.CharField(max_length=100)

    license_number = models.CharField(max_length=50)

    def __str__(self):
        return self.user.get_full_name()


class Availability(models.Model):

    DAYS = (
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
        ('SUNDAY', 'Sunday'),
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    day = models.CharField(
        max_length=20,
        choices=DAYS
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    slot_duration = models.IntegerField(
        default=30,
        help_text="minutes"
    )

    def __str__(self):
        return f"{self.doctor} - {self.day}"