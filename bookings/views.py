from datetime import timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from appointments.models import Appointment


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