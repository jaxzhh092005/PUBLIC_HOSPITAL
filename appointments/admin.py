from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "specialization", "appointment_date", "status", "created_at")
    list_filter = ("status", "specialization", "appointment_date")
    search_fields = ("last_name", "first_name", "email", "contact_number")