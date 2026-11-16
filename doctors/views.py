from datetime import date

from django.db.models import Q
from django.shortcuts import render

from appointments.models import Appointment
from hospitals.models import Hospital
from .models import Doctor


def doctor_list(request):
    doctors = Doctor.objects.select_related("user", "hospital")
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "")

    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(specialization__icontains=query)
            | Q(hospital__name__icontains=query)
        )
    if location:
        doctors = doctors.filter(hospital_id=location)

    return render(request, "doctors/list.html", {
        "doctors": doctors.order_by("user__last_name", "user__first_name"),
        "q": query,
        "location": location,
        "hospitals": Hospital.objects.order_by("name"),
    })


def doctor_dashboard(request):
    appointments = Appointment.objects.filter(
        doctor__user=request.user,
        appointment_date=date.today(),
    )
    return render(
        request,
        'doctors/dashboard.html',
        {'appointments': appointments},
    )