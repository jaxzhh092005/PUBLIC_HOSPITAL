from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render

from accounts.models import Profile
from appointments.models import Appointment
from doctors.models import Doctor
from hospitals.models import Hospital


class DoctorCreateForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "given-name"}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "family-name"}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.none())
    specialization = forms.CharField(max_length=100)
    license_number = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password_confirm = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hospital"].queryset = Hospital.objects.order_by("name")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        user_model = get_user_model()
        if user_model.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("An account with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        user_model = get_user_model()
        if user_model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "The passwords do not match.")

        if password and not self.has_error("password_confirm"):
            user_model = get_user_model()
            candidate = user_model(
                username=cleaned_data.get("username", ""),
                first_name=cleaned_data.get("first_name", ""),
                last_name=cleaned_data.get("last_name", ""),
                email=cleaned_data.get("email", ""),
            )
            try:
                validate_password(password, user=candidate)
            except ValidationError as error:
                self.add_error("password", error)
        return cleaned_data

    def save(self):
        if not self.is_valid():
            raise ValueError("DoctorCreateForm must be valid before saving.")

        user_model = get_user_model()
        with transaction.atomic():
            user = user_model.objects.create_user(
                username=self.cleaned_data["username"],
                email=self.cleaned_data["email"],
                password=self.cleaned_data["password"],
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                role="DOCTOR",
            )
            Profile.objects.create(user=user)
            return Doctor.objects.create(
                user=user,
                hospital=self.cleaned_data["hospital"],
                specialization=self.cleaned_data["specialization"],
                license_number=self.cleaned_data["license_number"],
            )


@staff_member_required
def dashboard(request):
    stats = []
    if request.user.has_perm("doctors.view_doctor"):
        stats.append({"label": "Doctors", "value": Doctor.objects.count(), "icon": "DR"})
    if request.user.has_perm("appointments.view_appointment"):
        stats.append({
            "label": "Pending appointments",
            "value": Appointment.objects.filter(status=Appointment.Status.PENDING).count(),
            "icon": "AP",
        })
    if request.user.has_perm("hospitals.view_hospital"):
        stats.append({"label": "Hospitals", "value": Hospital.objects.count(), "icon": "H"})
    if request.user.has_perm("accounts.view_user"):
        stats.append({"label": "Accounts", "value": get_user_model().objects.count(), "icon": "AC"})

    recent_appointments = []
    if request.user.has_perm("appointments.view_appointment"):
        recent_appointments = Appointment.objects.order_by("-created_at")[:6]

    return render(request, "hospital_admin/dashboard.html", {
        "stats": stats,
        "recent_appointments": recent_appointments,
    })


@staff_member_required
@permission_required("doctors.view_doctor", raise_exception=True)
def doctor_list(request):
    search = request.GET.get("q", "").strip()
    doctors = Doctor.objects.select_related("user", "hospital")
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
            | Q(specialization__icontains=search)
            | Q(license_number__icontains=search)
            | Q(hospital__name__icontains=search)
        )
    page_obj = Paginator(doctors.order_by("user__last_name", "user__first_name"), 12).get_page(
        request.GET.get("page")
    )
    return render(request, "hospital_admin/doctors.html", {
        "page_obj": page_obj,
        "search": search,
    })


@staff_member_required
@permission_required(("doctors.add_doctor", "accounts.add_user"), raise_exception=True)
def doctor_create(request):
    if not Hospital.objects.exists():
        messages.error(request, "Add a hospital before creating a doctor profile.")
        return redirect("admin:hospitals_hospital_add")

    form = DoctorCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        doctor = form.save()
        messages.success(request, f"{doctor} was added successfully.")
        return redirect("admin-doctors")
    return render(request, "hospital_admin/doctor_form.html", {"form": form})
