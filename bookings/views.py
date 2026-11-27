from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from appointments.models import Appointment
from doctors.models import Availability, Doctor

from .forms import RescheduleDateForm


def _my_appointments(request):
    """Only the patient's own bookings: their account's, plus ones made in this browser session."""
    ids = request.session.get("my_appointments", [])
    owned = Q(pk__in=ids)
    if request.user.is_authenticated:
        owned |= Q(user=request.user)
    return Appointment.objects.filter(owned)


def booking_list(request):
    appointments = _my_appointments(request)
    qs = appointments
    query = request.GET.get("q", "").strip()
    selected_hospital = request.GET.get("hospital", "").strip()
    status = request.GET.get("status", "")

    if query:
        qs = qs.filter(
            Q(doctor_name__icontains=query) | Q(specialization__icontains=query)
            | Q(hospital_name__icontains=query)
        )
    if selected_hospital:
        qs = qs.filter(hospital_name=selected_hospital)
    if status in Appointment.Status.values:
        qs = qs.filter(status=status)

    return render(request, "bookings/list.html", {
        "appointments": qs.order_by("appointment_date", "appointment_time"),
        "q": query,
        "hospitals": appointments.exclude(hospital_name="").order_by("hospital_name")
        .values_list("hospital_name", flat=True).distinct(),
        "selected_hospital": selected_hospital,
        "status": status,
        "statuses": Appointment.Status.choices,
        "today": timezone.localdate(),
        "tomorrow": timezone.localdate() + timedelta(days=1),
    })


def booking_detail(request, pk):
    appointment = get_object_or_404(_my_appointments(request), pk=pk)
    return render(request, "bookings/detail.html", {"a": appointment})


def _available_weekdays(appointment):
    doctors = Doctor.objects.select_related("user").filter(
        specialization__iexact=appointment.specialization,
    )
    if appointment.hospital_name:
        doctors = doctors.filter(hospital__name__iexact=appointment.hospital_name)

    if appointment.doctor_name:
        assigned_name = appointment.doctor_name.strip().casefold()
        matching_ids = []
        for doctor in doctors:
            full_name = doctor.user.get_full_name().strip()
            username = doctor.user.username.strip()
            aliases = {
                username.casefold(),
                full_name.casefold(),
                f"Dr. {full_name or username}".casefold(),
            }
            if assigned_name in aliases:
                matching_ids.append(doctor.pk)
        doctors = doctors.filter(pk__in=matching_ids)

    schedules = Availability.objects.filter(doctor__in=doctors)
    if appointment.appointment_time:
        schedules = schedules.filter(
            start_time__lte=appointment.appointment_time,
            end_time__gt=appointment.appointment_time,
        )
    return set(schedules.values_list("day", flat=True))


@login_required(login_url="signin:login")
def reschedule(request, pk):
    appointment = get_object_or_404(_my_appointments(request), pk=pk)
    if (
        appointment.status == Appointment.Status.CANCELLED
        or appointment.appointment_date < timezone.localdate()
    ):
        messages.error(request, "Only upcoming appointments can be rescheduled.")
        return redirect("bookings:detail", pk=appointment.pk)

    available_days = _available_weekdays(appointment)
    available_day_labels = [
        label for value, label in Availability.DAYS if value in available_days
    ]
    form = None
    if available_days:
        form = RescheduleDateForm(
            request.POST or None,
            available_days=available_days,
            current_date=appointment.appointment_date,
        )
        if request.method == "POST" and form.is_valid():
            appointment.appointment_date = form.cleaned_data["date"]
            appointment.save(update_fields=("appointment_date",))
            messages.success(request, "Your appointment date has been updated.")
            return redirect("bookings:detail", pk=appointment.pk)

    return render(request, "bookings/reschedule.html", {
        "a": appointment,
        "form": form,
        "available_days": available_day_labels,
    })