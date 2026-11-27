from django import forms
from django.utils import timezone


class RescheduleDateForm(forms.Form):
    date = forms.DateField(
        label="New appointment date",
        error_messages={
            "required": "Please select a new date.",
            "invalid": "Enter a valid date.",
        },
        widget=forms.DateInput(attrs={
            "class": "field-select field-date",
            "type": "date",
        }),
    )

    def __init__(self, *args, available_days, current_date, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_days = set(available_days)
        self.current_date = current_date
        self.fields["date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_date(self):
        value = self.cleaned_data["date"]
        if value < timezone.localdate():
            raise forms.ValidationError("Please choose today or a future date.")
        if value == self.current_date:
            raise forms.ValidationError("Choose a different date from your current appointment.")
        if value.strftime("%A").upper() not in self.available_days:
            raise forms.ValidationError(
                "The doctor is not available on this date. Choose one of the listed weekdays."
            )
        return value
