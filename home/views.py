from django.shortcuts import redirect, render


def home(request):
    if request.method == "POST":
        request.session["appointment_type"] = request.POST.get(
            "appointment_type",
            "clinical",
        )
        return redirect("appointments:step1")
    return render(request, "home/home.html")