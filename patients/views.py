from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from appointments.models import Appointment
from patients.models import Patient


@login_required(login_url='signin:login')
def patient_dashboard(request):
    patient = Patient.objects.filter(user=request.user).select_related('user').first()
    appointments = []
    if patient:
        appointments = Appointment.objects.filter(user=request.user).order_by('-appointment_date', '-created_at')
    return render(request, 'patients/dashboard.html', {
        'patient': patient,
        'appointments': appointments,
    })
