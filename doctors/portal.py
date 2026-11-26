from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from appointments.models import Appointment
from files.models import MedicalFile

from .models import Availability, Doctor


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ("day", "start_time", "end_time", "slot_duration")
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "end_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "slot_duration": forms.NumberInput(attrs={"min": 5, "step": 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "End time must be later than start time.")
        return cleaned_data


AvailabilityFormSet = modelformset_factory(
    Availability,
    form=AvailabilityForm,
    extra=1,
    can_delete=True,
)


def _doctor_for_user(user):
    if user.role != "DOCTOR":
        raise PermissionDenied
    return get_object_or_404(Doctor.objects.select_related("user", "hospital"), user=user)


def _assigned_appointments(doctor):
    full_name = doctor.user.get_full_name().strip()
    names = {doctor.user.username, f"Dr. {full_name}"}
    if full_name:
        names.add(full_name)
    assigned_to_doctor = Q()
    for name in names:
        assigned_to_doctor |= Q(doctor_name__iexact=name)
    return Appointment.objects.filter(assigned_to_doctor)


def _queue_appointments(doctor):
    return Appointment.objects.filter(
        doctor_name="",
        hospital_name__iexact=doctor.hospital.name,
        specialization__iexact=doctor.specialization,
        status=Appointment.Status.PENDING,
        appointment_date__gte=timezone.localdate(),
    )


@login_required(login_url="signin:login")
def doctor_dashboard(request):
    doctor = _doctor_for_user(request.user)
    section = request.GET.get("section", "appointments")
    if section not in {"appointments", "records", "queue", "availability"}:
        section = "appointments"

    today = timezone.localdate()
    context = {
        "doctor": doctor,
        "section": section,
        "today": today,
    }

    if section == "appointments":
        appointment_view = request.GET.get("view", "today")
        if appointment_view not in {"today", "upcoming", "completed"}:
            appointment_view = "today"
        appointments = _assigned_appointments(doctor)
        if appointment_view == "today":
            appointments = appointments.filter(appointment_date=today)
        elif appointment_view == "upcoming":
            appointments = appointments.filter(appointment_date__gt=today)
        else:
            appointments = appointments.filter(appointment_date__lt=today)
        context.update({
            "appointment_view": appointment_view,
            "appointments": appointments.order_by("appointment_date", "appointment_time"),
        })
    elif section == "queue":
        context["queue"] = _queue_appointments(doctor).order_by(
            "appointment_date", "appointment_time", "created_at"
        )
    elif section == "records":
        assigned = _assigned_appointments(doctor)
        search = request.GET.get("q", "").strip()
        records = assigned
        if search:
            records = records.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(contact_number__icontains=search)
            )
        context.update({
            "search": search,
            "records": records.order_by("-appointment_date", "-appointment_time"),
            "medical_files": MedicalFile.objects.filter(
                patient__user__appointments__in=assigned
            ).select_related("patient__user").distinct().order_by("-uploaded_at"),
        })
    else:
        formset = AvailabilityFormSet(
            request.POST or None,
            queryset=Availability.objects.filter(doctor=doctor).order_by("day", "start_time"),
            prefix="availability",
        )
        if request.method == "POST":
            if formset.is_valid():
                with transaction.atomic():
                    schedules = formset.save(commit=False)
                    for deleted in formset.deleted_objects:
                        deleted.delete()
                    for schedule in schedules:
                        schedule.doctor = doctor
                        schedule.save()
                messages.success(request, "Your weekly availability was saved.")
                return redirect(f"{reverse('doctor-dashboard')}?section=availability")
            messages.error(request, "Check the schedule details and try again.")
        context["availability_formset"] = formset

    return render(request, "doctor_portal/dashboard.html", context)


@login_required(login_url="signin:login")
@require_POST
def accept_appointment(request, appointment_id):
    doctor = _doctor_for_user(request.user)
    with transaction.atomic():
        appointment = get_object_or_404(
            _queue_appointments(doctor).select_for_update(),
            pk=appointment_id,
        )
        appointment.doctor_name = f"Dr. {doctor.user.get_full_name() or doctor.user.username}"
        appointment.hospital_name = doctor.hospital.name
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save(update_fields=("doctor_name", "hospital_name", "status"))
    messages.success(request, f"Appointment for {appointment.first_name} {appointment.last_name} accepted.")
    return HttpResponseRedirect(f"{reverse('doctor-dashboard')}?section=queue")
