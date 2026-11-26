from django import forms
from django.contrib import admin
from .models import Availability, Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", "hospital", "specialization", "license_number")
    list_filter = ("hospital", "specialization")
    search_fields = ("user__username", "user__first_name", "user__last_name", "license_number")


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("doctor", "day", "start_time", "end_time", "slot_duration")
    list_filter = ("day", "doctor__hospital")
    search_fields = ("doctor__user__username", "doctor__user__first_name", "doctor__user__last_name")

