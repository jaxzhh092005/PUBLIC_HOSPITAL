from django.shortcuts import render

def landing(request):
    return render(request, "page/landing.html", {
        "specialties": ["Primary Care", "Cardiology", "Pediatrics"],
    })