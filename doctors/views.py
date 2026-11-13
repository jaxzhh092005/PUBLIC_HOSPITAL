from datetime import date

from django.shortcuts import render

from appointments.models import Appointment


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