import re

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

INPUT = {"class": "acc-input"}


class AccountForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=150, widget=forms.TextInput(attrs=INPUT),
                                 error_messages={"required": "First name is required."})
    middle_name = forms.CharField(label="Middle Name", max_length=60, required=False,
                                  widget=forms.TextInput(attrs=INPUT))
    last_name = forms.CharField(label="Last Name", max_length=150, widget=forms.TextInput(attrs=INPUT),
                                error_messages={"required": "Last name is required."})
    birthdate = forms.DateField(label="Birthdate", required=False,
                                widget=forms.DateInput(attrs={**INPUT, "type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["birthdate"].widget.attrs["max"] = timezone.localdate().isoformat()

    def clean_birthdate(self):
        value = self.cleaned_data.get("birthdate")
        if value and value > timezone.localdate():
            raise forms.ValidationError("Birthdate cannot be in the future.")
        return value


class _PasswordConfirmForm(forms.Form):
    """Changing contact details needs the current password, so a stolen session can't hijack the account."""
    password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={**INPUT, "autocomplete": "current-password"}),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        pw = self.cleaned_data["password"]
        if not self.user.check_password(pw):
            raise forms.ValidationError("Incorrect password.")
        return pw


class MobileChangeForm(_PasswordConfirmForm):
    mobile = forms.CharField(
        label="New mobile number", max_length=20,
        widget=forms.TextInput(attrs={**INPUT, "inputmode": "tel", "placeholder": "9123456789"}),
    )
    field_order = ["mobile", "password"]

    def clean_mobile(self):
        raw = re.sub(r"[\s-]", "", self.cleaned_data["mobile"])
        for prefix in ("+63", "0"):
            if raw.startswith(prefix):
                raw = raw[len(prefix):]
                break
        if not re.fullmatch(r"9\d{9}", raw):
            raise forms.ValidationError("Enter a valid Philippine mobile number, e.g. 9123456789.")
        return "+63" + raw


class EmailChangeForm(_PasswordConfirmForm):
    email = forms.EmailField(label="New email", widget=forms.EmailInput(attrs=INPUT))
    field_order = ["email", "password"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("That email is already used by another account.")
        return email