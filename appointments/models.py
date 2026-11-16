from django.conf import settings
from django.db import models


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    # Who can see this booking (set when the patient is logged in)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name="appointments")

    # Assigned by hospital staff after the request is reviewed
    doctor_name = models.CharField(max_length=120, blank=True)
    doctor_photo = models.ImageField(upload_to="doctor_photos/", blank=True)
    hospital_name = models.CharField(max_length=150, blank=True)

    # Step 1-2
    specialization = models.CharField(max_length=60)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(null=True, blank=True)  # assigned by the hospital

    # Step 3
    last_name = models.CharField(max_length=60)
    first_name = models.CharField(max_length=60)
    middle_name = models.CharField(max_length=60, blank=True)
    suffix = models.CharField(max_length=10, blank=True)
    birthdate = models.DateField()
    gender = models.CharField(max_length=30)
    email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    region = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    barangay = models.CharField(max_length=80)
    street = models.CharField(max_length=150)

    # Step 4
    valid_id = models.FileField(upload_to="appointment_ids/")

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def title(self):
        return {
            self.Status.CONFIRMED: "Scheduled Check-Up",
            self.Status.CANCELLED: "Cancelled Appointment",
        }.get(self.status, "Appointment Request")

    def __str__(self):
        return f"{self.last_name}, {self.first_name} – {self.specialization} on {self.appointment_date}"