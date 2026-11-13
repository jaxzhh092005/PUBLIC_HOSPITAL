from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from appointments.models import Appointment
from .models import Nurse


@login_required
def nurse_dashboard(request):
    nurse = get_object_or_404(
        Nurse.objects.select_related('hospital'),
        user=request.user,
    )
    appointments = (
        Appointment.objects.filter(
            doctor__hospital=nurse.hospital,
            appointment_date__gte=timezone.localdate(),
        )
        .select_related('patient__user', 'doctor__user')
        .order_by('appointment_date', 'appointment_time')
    )
    return render(
        request,
        'nurse/dashboard.html',
        {
            'nurse': nurse,
            'appointments': appointments,
            'today': timezone.localdate(),
        },
    )
