from datetime import date

from django.contrib.auth import get_user_model
from django.conf import settings
from django.conf.urls.static import static
from django.test import TestCase, override_settings
from django.urls import reverse

from appointments.models import Appointment


class BookingAccessTests(TestCase):
    def create_appointment(self, specialization, user=None):
        return Appointment.objects.create(
            user=user,
            specialization=specialization,
            appointment_date=date.today(),
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

    def test_patient_cannot_open_another_accounts_booking(self):
        patient = get_user_model().objects.create_user(username="patient", password="test")
        other_user = get_user_model().objects.create_user(username="other", password="test")
        other_booking = self.create_appointment("OTHER_BOOKING", other_user)
        self.client.force_login(patient)

        response = self.client.get(reverse("bookings:detail", args=[other_booking.pk]))

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
