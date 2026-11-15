from datetime import date

from django.shortcuts import redirect, render

from .forms import DateForm, InformationForm, SpecializationForm
from .steps import STEPS, get_step, next_url_name, prev_url_name


def _context(number, **extra):
    return {
        "steps": STEPS,
        "current": number,
        "step": get_step(number),
        "back_url": prev_url_name(number),
        **extra,
    }


def step1(request):
    initial = {"specialization": request.session.get("specialization", "")}
    form = SpecializationForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        request.session["specialization"] = form.cleaned_data["specialization"]
        return redirect(next_url_name(1))

    return render(request, "appointments/step1.html", _context(1, form=form))


def step2(request):
    # Steps must be done in order: send the patient back if step 1 is missing.
    if not request.session.get("specialization"):
        return redirect("appointments:step1")

    saved = request.session.get("appointment_date")
    initial = {"date": date.fromisoformat(saved)} if saved else None
    form = DateForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        request.session["appointment_date"] = form.cleaned_data["date"].isoformat()
        return redirect(next_url_name(2))

    return render(request, "appointments/step2.html", _context(2, form=form))


def step3(request):
    if not request.session.get("appointment_date"):
        return redirect("appointments:step2")

    saved = request.session.get("patient_info")
    initial = None
    if saved:
        initial = {**saved, "birthdate": date.fromisoformat(saved["birthdate"])}
    form = InformationForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        data["birthdate"] = data["birthdate"].isoformat()  # sessions store JSON
        request.session["patient_info"] = data
        return redirect(next_url_name(3))

    return render(request, "appointments/step3.html", _context(3, form=form))


def placeholder_step(number):
    """Steps 4-5 share the same shell until their forms are built."""
    def view(request):
        if request.method == "POST":
            return redirect(next_url_name(number))
        return render(request, "appointments/step_placeholder.html", _context(number))
    return view