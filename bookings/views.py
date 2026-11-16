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
    qs = _my_appointments(request)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if query:
        qs = qs.filter(
            Q(doctor_name__icontains=query) | Q(specialization__icontains=query)
            | Q(hospital_name__icontains=query)
        )
    if status in Appointment.Status.values:
        qs = qs.filter(status=status)

    return render(request, "bookings/list.html", {
        "appointments": qs.order_by("appointment_date", "appointment_time"),
        "q": query,
        "status": status,
        "statuses": Appointment.Status.choices,
        "today": timezone.localdate(),
        "tomorrow": timezone.localdate() + timedelta(days=1),
    })


def booking_detail(request, pk):
    appointment = get_object_or_404(_my_appointments(request), pk=pk)
    return render(request, "bookings/detail.html", {"a": appointment})