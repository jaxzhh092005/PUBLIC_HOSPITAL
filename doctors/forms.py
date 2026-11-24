from django import forms

class DoctorSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="Search doctors",
        widget=forms.TextInput(attrs={
            "type": "search",
            "placeholder": "Search by specialty, hospital, or doctor name",
            "aria-label": "Search doctors",
        }),
    )
    specialty = forms.CharField(required=False, widget=forms.HiddenInput())