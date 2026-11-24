from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "birthdate", "gender", "mobile")
    list_filter = ("gender",)
    search_fields = ("user__username", "user__email", "mobile", "emergency_contact")
