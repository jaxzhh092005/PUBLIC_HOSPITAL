from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

from .models import Availability, Doctor

User = get_user_model()


class DoctorAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Doctor
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # optional details: only first name, last name and hospital are needed
        for name in ("specialization", "license_number"):
            if name in self.fields:
                self.fields[name].required = False
        # when editing, show the current names
        if self.instance.pk:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def _make_username(self, first, last):
        base = slugify(f"{first}.{last}").replace("-", ".") or "doctor"
        username, n = base, 1
        while User.objects.filter(username=username).exists():
            n += 1
            username = f"{base}{n}"
        return username

    @transaction.atomic
    def save(self, commit=True):
        doctor = super().save(commit=False)
        first = self.cleaned_data["first_name"].strip()
        last = self.cleaned_data["last_name"].strip()

        if doctor.pk:                      # editing: update the linked user's name
            user = doctor.user
            user.first_name, user.last_name = first, last
            user.save()
        else:                              # new doctor: create a login-less user
            user = User(username=self._make_username(first, last),
                        first_name=first, last_name=last)
            user.set_unusable_password()
            user.save()
            doctor.user = user

        if commit:
            doctor.save()
            self.save_m2m()
        return doctor


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm
    fields = ("first_name", "last_name", "hospital", "specialization", "license_number")
    list_display = ("__str__", "specialization", "hospital", "license_number")
    list_filter = ("specialization", "hospital")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "specialization",
        "license_number",
    )
    inlines = (AvailabilityInline,)


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("doctor", "day", "start_time", "end_time", "slot_duration")
    list_filter = ("day", "doctor")