from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.conf.urls.static import static
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment
from doctors.models import Availability, Doctor
from hospitals.models import Hospital


class BookingAccessTests(TestCase):
    def create_appointment(
        self,
        specialization,
        user=None,
        hospital_name="",
        doctor_name="",
        appointment_date=None,
    ):
        return Appointment.objects.create(
            user=user,
            specialization=specialization,
            doctor_name=doctor_name,
            hospital_name=hospital_name,
            appointment_date=appointment_date or timezone.localdate(),
            last_name="Patient",
            first_name="Test",
            birthdate=date(1990, 1, 1),
            gender="Prefer not to say",
            email="patient@example.com",
            contact_number="09123456789",
            region="Region",
            province="Province",
            municipality="Municipality",
            barangay="Barangay",
            street="Street",
            valid_id="appointment_ids/test.png",
        )

    def create_doctor_with_monday_availability(self):
        user = get_user_model().objects.create_user(
            username="doctor",
            first_name="Morgan",
            last_name="Lee",
        )
        hospital = Hospital.objects.create(
            name="Central Hospital",
            address="Main Street",
            phone="123456789",
        )
        doctor = Doctor.objects.create(
            user=user,
            hospital=hospital,
            specialization="Cardiology",
            license_number="LIC-001",
        )
        Availability.objects.create(
            doctor=doctor,
            day="MONDAY",
            start_time=time(9, 0),
            end_time=time(17, 0),
        )
        return hospital, doctor

    def next_weekday(self, weekday):
        today = timezone.localdate()
        days_ahead = (weekday - today.weekday()) % 7 or 7
        return today + timedelta(days=days_ahead)

    def test_booking_list_shows_account_and_session_bookings_only(self):
        user_model = get_user_model()
        patient = user_model.objects.create_user(username="patient", password="test")
        other_user = user_model.objects.create_user(username="other", password="test")
        self.create_appointment("ACCOUNT_BOOKING", patient)
        session_booking = self.create_appointment("SESSION_BOOKING")
        self.create_appointment("OTHER_BOOKING", other_user)

        self.client.force_login(patient)
        session = self.client.session
        session["my_appointments"] = [session_booking.pk]
        session.save()

        response = self.client.get(reverse("bookings:list"))

        self.assertContains(response, "ACCOUNT_BOOKING")
        self.assertContains(response, "SESSION_BOOKING")
        self.assertNotContains(response, "OTHER_BOOKING")

    def test_booking_list_filters_by_hospital(self):
        patient = get_user_model().objects.create_user(username="patient", password="test")
        self.create_appointment("GENERAL_MEDICINE", patient, hospital_name="North Hospital")
        self.create_appointment("PEDIATRICS", patient, hospital_name="South Hospital")
        self.client.force_login(patient)

        response = self.client.get(reverse("bookings:list"), {"hospital": "North Hospital"})

        self.assertContains(response, "GENERAL_MEDICINE")
        self.assertNotContains(response, "PEDIATRICS")
        self.assertContains(response, 'option value="North Hospital" selected')

    def test_patient_cannot_open_another_accounts_booking(self):
        patient = get_user_model().objects.create_user(username="patient", password="test")
        other_user = get_user_model().objects.create_user(username="other", password="test")
        other_booking = self.create_appointment("OTHER_BOOKING", other_user)
        self.client.force_login(patient)

        response = self.client.get(reverse("bookings:detail", args=[other_booking.pk]))

        self.assertEqual(response.status_code, 404)

    def test_reschedule_requires_login_and_returns_to_selected_appointment(self):
        appointment = self.create_appointment("Cardiology")
        session = self.client.session
        session["my_appointments"] = [appointment.pk]
        session.save()
        reschedule_url = reverse("bookings:reschedule", args=[appointment.pk])

        response = self.client.get(reschedule_url)

        self.assertRedirects(
            response,
            f'{reverse("signin:login")}?next={reschedule_url}',
            fetch_redirect_response=False,
        )

    def test_reschedule_updates_the_existing_appointment_on_doctor_available_day(self):
        patient = get_user_model().objects.create_user(username="patient")
        hospital, _doctor = self.create_doctor_with_monday_availability()
        available_date = self.next_weekday(0)
        appointment = self.create_appointment(
            "Cardiology",
            user=patient,
            hospital_name=hospital.name,
            doctor_name="Dr. Morgan Lee",
            appointment_date=available_date + timedelta(days=7),
        )
        self.client.force_login(patient)

        response = self.client.post(
            reverse("bookings:reschedule", args=[appointment.pk]),
            {"date": available_date.isoformat()},
        )

        self.assertRedirects(
            response,
            reverse("bookings:detail", args=[appointment.pk]),
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.appointment_date, available_date)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_reschedule_rejects_dates_when_doctor_is_unavailable(self):
        patient = get_user_model().objects.create_user(username="patient")
        hospital, _doctor = self.create_doctor_with_monday_availability()
        available_date = self.next_weekday(0)
        current_date = available_date + timedelta(days=7)
        appointment = self.create_appointment(
            "Cardiology",
            user=patient,
            hospital_name=hospital.name,
            doctor_name="Dr. Morgan Lee",
            appointment_date=current_date,
        )
        unavailable_date = available_date + timedelta(days=1)
        self.client.force_login(patient)

        response = self.client.post(
            reverse("bookings:reschedule", args=[appointment.pk]),
            {"date": unavailable_date.isoformat()},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The doctor is not available on this date.")
        appointment.refresh_from_db()
        self.assertEqual(appointment.appointment_date, current_date)

    def test_reschedule_is_limited_to_the_patient_own_appointment(self):
        patient = get_user_model().objects.create_user(username="patient")
        other_patient = get_user_model().objects.create_user(username="other-patient")
        appointment = self.create_appointment("Cardiology", user=other_patient)
        self.client.force_login(patient)

        response = self.client.get(
            reverse("bookings:reschedule", args=[appointment.pk]),
        )

        self.assertEqual(response.status_code, 404)

    def test_private_id_files_have_no_public_media_route(self):
        with override_settings(DEBUG=True):
            media_patterns = static(
                settings.MEDIA_URL + "doctor_photos/",
                document_root=settings.MEDIA_ROOT / "doctor_photos",
            )

        route = media_patterns[0].pattern.regex
        self.assertIsNotNone(route.match("media/doctor_photos/profile.png"))
        self.assertIsNone(route.match("media/appointment_ids/private.png"))
