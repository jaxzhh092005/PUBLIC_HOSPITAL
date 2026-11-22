from django.contrib import admin

from .models import Nurse, VitalSign


@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ("user", "hospital")
    list_filter = ("hospital",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "hospital__name")


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ("patient", "temperature", "blood_pressure", "pulse_rate", "oxygen", "created_at")
    list_filter = ("created_at",)
    search_fields = ("patient__user__username", "patient__user__first_name", "patient__user__last_name")
