from datetime import date

import os
import uuid

from django.core.files.storage import default_storage
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import SPECIALIZATIONS, DateForm, DocumentsForm, InformationForm, SpecializationForm
from .models import Appointment
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


def step4(request):
    if not request.session.get("patient_info"):
        return redirect("appointments:step3")

    existing = request.session.get("valid_id")
    if existing and not default_storage.exists(existing["path"]):
        existing = None  # file was cleaned up; ask again
        request.session.pop("valid_id", None)

    form = DocumentsForm(request.POST or None, request.FILES or None, has_existing=bool(existing))

    if request.method == "POST" and form.is_valid():
        upload = form.cleaned_data["valid_id"]
        if upload:
            if existing:
                default_storage.delete(existing["path"])
            ext = ".png" if upload.image.format == "PNG" else ".jpg"
            path = default_storage.save(f"appointment_ids/{uuid.uuid4().hex}{ext}", upload)
            request.session["valid_id"] = {"path": path, "name": os.path.basename(upload.name)}
        return redirect(next_url_name(4))

    return render(request, "appointments/step4.html", _context(4, form=form, existing=existing))


SESSION_KEYS = ("specialization", "appointment_date", "patient_info", "valid_id")


def step5(request):
    spec = request.session.get("specialization")
    appt_date = request.session.get("appointment_date")
    info = request.session.get("patient_info")
    id_file = request.session.get("valid_id")

    # Send the patient back to the first step that is still missing.
    for value, name in ((spec, "step1"), (appt_date, "step2"), (info, "step3"), (id_file, "step4")):
        if not value:
            return redirect(f"appointments:{name}")

    spec_label = dict(SPECIALIZATIONS).get(spec, spec)

    if request.method == "POST":
        with transaction.atomic():
            appt = Appointment.objects.create(
                user=request.user if request.user.is_authenticated else None,
                specialization=spec_label,
                appointment_date=date.fromisoformat(appt_date),
                last_name=info["last_name"],
                first_name=info["first_name"],
                middle_name=info.get("middle_name", ""),
                suffix=info.get("suffix", ""),
                birthdate=date.fromisoformat(info["birthdate"]),
                gender=info["gender"],
                email=info["email"],
                contact_number=info["contact_number"],
                region=info["region"],
                province=info["province"],
                municipality=info["municipality"],
                barangay=info["barangay"],
                street=info["street"],
                valid_id=id_file["path"],  # already saved in step 4
            )
        # Lets this browser see its own booking even without a login.
        request.session["my_appointments"] = [*request.session.get("my_appointments", []), appt.pk]
        for key in SESSION_KEYS:
            request.session.pop(key, None)
        messages.success(request, "Your appointment request has been submitted.")
        return redirect(next_url_name(5))

    name_parts = [info["first_name"], info.get("middle_name"), info["last_name"], info.get("suffix")]
    address_parts = [info["street"], info["barangay"], info["municipality"],
                     None if info["province"] == "N/A" else info["province"], info["region"]]
    review = {
        "specialization": spec_label,
        "date": date.fromisoformat(appt_date),
        "full_name": " ".join(p for p in name_parts if p),
        "birthdate": date.fromisoformat(info["birthdate"]),
        "gender": info["gender"],
        "email": info["email"],
        "mobile": info["contact_number"],
        "address": ", ".join(p for p in address_parts if p),
    }
    return render(request, "appointments/step5.html", _context(5, review=review))