from django import forms
from django.core.validators import RegexValidator
from django.utils import timezone

# Replace with a ModelChoiceField on your doctors' Specialization model when ready.
SPECIALIZATIONS = [
    ("", "—select specialization—"),
    ("general", "General Medicine"),
    ("pediatrics", "Pediatrics"),
    ("obgyn", "Obstetrics & Gynecology"),
    ("cardiology", "Cardiology"),
    ("dermatology", "Dermatology"),
    ("orthopedics", "Orthopedics"),
    ("ent", "Ear, Nose & Throat"),
    ("ophthalmology", "Ophthalmology"),
]


class SpecializationForm(forms.Form):
    specialization = forms.ChoiceField(
        label="Select Specialization",
        choices=SPECIALIZATIONS,
        error_messages={"required": "Please select a specialization to continue."},
        widget=forms.Select(attrs={"class": "field-select"}),
    )


class DateForm(forms.Form):
    date = forms.DateField(
        label="Select Date",
        error_messages={
            "required": "Please select a date to continue.",
            "invalid": "Enter a valid date.",
        },
        widget=forms.DateInput(attrs={"class": "field-select field-date", "type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Browsers block past dates in the picker; clean_date enforces it server-side.
        self.fields["date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_date(self):
        value = self.cleaned_data["date"]
        if value < timezone.localdate():
            raise forms.ValidationError("Please choose today or a future date.")
        return value


def _input(placeholder="", **attrs):
    return forms.TextInput(attrs={"class": "field-input", "placeholder": placeholder, **attrs})


def _select(placeholder):
    # Region / province / municipality options are loaded by JS (PSGC API),
    # so the server only checks that a value was submitted.
    return forms.Select(attrs={"class": "field-select"}, choices=[("", placeholder)])


class InformationForm(forms.Form):
    SUFFIXES = [("", "— select —"), ("Jr.", "Jr."), ("Sr.", "Sr."),
                ("II", "II"), ("III", "III"), ("IV", "IV"), ("V", "V")]
    GENDERS = [("", "— select —"), ("Male", "Male"), ("Female", "Female"),
               ("Prefer not to say", "Prefer not to say")]
    REQ = "This field is required."

    last_name = forms.CharField(label="Last Name", max_length=60, widget=_input(),
                                error_messages={"required": REQ})
    first_name = forms.CharField(label="First Name", max_length=60, widget=_input(),
                                 error_messages={"required": REQ})
    middle_name = forms.CharField(label="Middle Name", max_length=60, required=False, widget=_input())

    suffix = forms.ChoiceField(label="Suffix", choices=SUFFIXES, required=False,
                               widget=forms.Select(attrs={"class": "field-select"}))
    birthdate = forms.DateField(label="Birthdate", error_messages={"required": REQ, "invalid": "Enter a valid date."},
                                widget=forms.DateInput(attrs={"class": "field-input field-date", "type": "date"}))
    gender = forms.ChoiceField(label="Gender", choices=GENDERS, error_messages={"required": REQ},
                               widget=forms.Select(attrs={"class": "field-select"}))

    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "field-input"}),
                             error_messages={"required": REQ, "invalid": "Enter a valid email address."})
    contact_number = forms.CharField(
        label="Contact Number", max_length=12, strip=False,
                                 widget=_input(
                                     "09XXXXXXXXX", inputmode="numeric", pattern="[0-9]*",
                                     **{"data-digits-only": "true"},
                                 ),
        validators=[RegexValidator(
            r"^(09[0-9]{9}|639[0-9]{9})$",
            "Use a Philippine mobile number, e.g. 09123456789.",
        )],
        error_messages={"required": REQ},
    )

    region = forms.CharField(label="Region", widget=_select("— select region —"), error_messages={"required": REQ})
    province = forms.CharField(label="Province", widget=_select("— select region —"), error_messages={"required": REQ})
    municipality = forms.CharField(label="Municipality", widget=_select("— select municipality —"),
                                   error_messages={"required": REQ})
    barangay = forms.CharField(label="Barangay", max_length=80, widget=_input(), error_messages={"required": REQ})
    street = forms.CharField(label="House No. / Street", max_length=150, widget=_input(),
                             error_messages={"required": REQ})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birthdate"].widget.attrs["max"] = timezone.localdate().isoformat()

    def clean_birthdate(self):
        value = self.cleaned_data["birthdate"]
        if value > timezone.localdate():
            raise forms.ValidationError("Birthdate cannot be in the future.")
        return value


class DocumentsForm(forms.Form):
    MAX_BYTES = 10 * 1024 * 1024
    ALLOWED_FORMATS = {"JPEG", "PNG"}

    valid_id = forms.ImageField(
        label="Upload your Valid ID",
        required=False,  # enforced in clean_valid_id so a previous upload can satisfy it
        widget=forms.ClearableFileInput(attrs={
            "class": "dropzone-input", "accept": "image/jpeg,image/png",
        }),
        error_messages={"invalid_image": "Upload a valid JPEG or PNG image."},
    )

    def __init__(self, *args, has_existing=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_existing = has_existing

    def clean_valid_id(self):
        f = self.cleaned_data.get("valid_id")
        if not f:
            if self.has_existing:
                return None  # keep the file uploaded earlier
            raise forms.ValidationError("Please upload your valid ID to continue.")
        if f.size > self.MAX_BYTES:
            raise forms.ValidationError("File is too large. Maximum size is 10MB.")
        # ImageField has already opened it with Pillow; check the real format, not the extension.
        if getattr(f.image, "format", None) not in self.ALLOWED_FORMATS:
            raise forms.ValidationError("Only JPEG or PNG images are accepted.")
        return f