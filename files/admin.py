from django.contrib import admin

from .models import MedicalFile


@admin.register(MedicalFile)
class MedicalFileAdmin(admin.ModelAdmin):
    list_display = ("patient", "file_type", "uploaded_at")
    list_filter = ("file_type", "uploaded_at")
    search_fields = ("patient__user__username", "patient__user__email")
