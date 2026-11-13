from django.shortcuts import render

def specialization(request):

    return render(
        request,
        'appointments/specialization.html'
    )

def appointment_date(request):

    return render(
        request,
        'appointments/date.html'
    )
def doctor_selection(request):

    return render(
        request,
        'appointments/doctor.html'
    )

def information(request):

    return render(
        request,
        'appointments/information.html'
    )

def upload_documents(request):

    return render(
        request,
        'appointments/documents.html'
    )

def review(request):

    return render(
        request,
        'appointments/review.html'
    )

def confirmation(request):

    return render(
        request,
        'appointments/confirmation.html'
    )


