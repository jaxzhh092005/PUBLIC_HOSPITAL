from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile_number", "birthdate")
    search_fields = ("user__username", "user__email", "mobile_number")