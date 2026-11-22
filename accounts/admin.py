from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Profile, User


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile_number", "birthdate")
    search_fields = ("user__username", "user__email", "mobile_number")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Hospital role", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (None, {"classes": ("wide",), "fields": ("email", "role")}),
    )
    list_display = DjangoUserAdmin.list_display + ("role",)
    list_filter = DjangoUserAdmin.list_filter + ("role",)