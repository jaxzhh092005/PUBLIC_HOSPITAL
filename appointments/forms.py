from django import forms

class AppointmentStep1Form(forms.Form):

    specialization = forms.CharField()

class AppointmentStep2Form(forms.Form):

    appointment_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type':'date'}
        )
    )

class AppointmentStep3Form(forms.Form):

    doctor = forms.IntegerField()

    time_slot = forms.TimeField()

class AppointmentStep4Form(forms.Form):

    reason = forms.CharField(
        widget=forms.Textarea
    )

class AppointmentStep5Form(forms.Form):

    valid_id = forms.FileField()

    laboratory = forms.FileField(
        required=False
    )