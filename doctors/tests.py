from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment
from hospitals.models import Hospital
from .models import Availability, Doctor


class DoctorListTests(TestCase):
    def test_doctors_page_lists_doctors_and_uses_shared_navbar(self):
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

        response = self.client.get(reverse("doctors:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Morgan Lee")
        self.assertContains(response, "Cardiology")
        self.assertContains(response, "Weekly availability")
        self.assertContains(response, reverse("doctors:profile", args=[doctor.pk]))
        self.assertContains(response, reverse("doctors:list"))
        self.assertContains(response, 'aria-current="page"', count=1)

    def test_doctor_profile_shows_doctor_and_weekly_availability(self):
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
            end_time=time(12, 0),
        )

        response = self.client.get(reverse("doctors:profile", args=[doctor.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Morgan Lee")
        self.assertContains(response, "Central Hospital")
        self.assertContains(response, "Monday")
        self.assertContains(response, "9:00 AM")

    def test_doctor_list_searches_by_specialization(self):
        hospital = Hospital.objects.create(
            name="Central Hospital",
            address="Main Street",
            phone="123456789",
        )
        card_user = get_user_model().objects.create_user(username="cardiology")
        neuro_user = get_user_model().objects.create_user(username="neurology")
        Doctor.objects.create(
            user=card_user,
            hospital=hospital,
            specialization="Cardiology",
            license_number="LIC-CARD",
        )
        Doctor.objects.create(
            user=neuro_user,
            hospital=hospital,
            specialization="Neurology",
            license_number="LIC-NEUR",
        )

        response = self.client.get(
            reverse("doctors:list"),
            {"q": "Cardiology"},
        )

        self.assertContains(response, "Dr. cardiology")
        self.assertNotContains(response, "Dr. neurology")

    def test_public_doctor_list_filters_by_specialty_from_category_link(self):
        hospital = Hospital.objects.create(
            name="Central Hospital",
            address="Main Street",
            phone="123456789",
        )
        endocrinologist = get_user_model().objects.create_user(
            username="endocrinologist",
        )
        cardiologist = get_user_model().objects.create_user(username="cardiologist")
        Doctor.objects.create(
            user=endocrinologist,
            hospital=hospital,
            specialization="Endocrinology",
            license_number="LIC-ENDO",
        )
        Doctor.objects.create(
            user=cardiologist,
            hospital=hospital,
            specialization="Cardiology",
            license_number="LIC-CARD",
        )

        response = self.client.get(
            reverse("doctors:list"),
            {"specialty": "Endocrinology"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. endocrinologist")
        self.assertNotContains(response, "Dr. cardiologist")
        self.assertContains(response, 'name="specialty" value="Endocrinology"')

    def test_doctor_list_paginates_and_keeps_specialty_filter(self):
        hospital = Hospital.objects.create(
            name="Central Hospital",
            address="Main Street",
            phone="123456789",
        )
        for index in range(7):
            user = get_user_model().objects.create_user(
                username=f"general-doctor-{index}",
            )
            Doctor.objects.create(
                user=user,
                hospital=hospital,
                specialization="General Medicine",
                license_number=f"LIC-GEN-{index}",
            )

        response = self.client.get(
            reverse("doctors:list"),
            {"specialty": "General Medicine"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 1)
        self.assertEqual(len(response.context["doctors"]), 6)
        self.assertContains(
            response,
            'href="?specialty=General+Medicine&amp;page=2"',
        )

        response = self.client.get(
            reverse("doctors:list"),
            {"specialty": "General Medicine", "page": 2},
        )

        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["doctors"]), 1)
        self.assertContains(
            response,
            'href="?specialty=General+Medicine&amp;page=1"',
        )


class DoctorPortalTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="morgan.lee",
            email="morgan@example.com",
            password="DoctorPass!9284",
            first_name="Morgan",
            last_name="Lee",
            role="DOCTOR",
        )
        self.hospital = Hospital.objects.create(
            name="Central Hospital",
            address="Main Street",
            phone="123456789",
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            hospital=self.hospital,
            specialization="Cardiology",
            license_number="LIC-001",
        )

    def create_appointment(self, **overrides):
        values = {
            "specialization": self.doctor.specialization,
            "appointment_date": timezone.localdate(),
            "last_name": "Patient",
            "first_name": "Taylor",
            "birthdate": date(1990, 1, 1),
            "gender": "Other",
            "email": "taylor@example.com",
            "contact_number": "09123456789",
            "region": "Region",
            "province": "Province",
            "municipality": "Town",
            "barangay": "Barangay",
            "street": "Main Street",
            "valid_id": "appointment_ids/test.png",
            "hospital_name": self.hospital.name,
        }
        values.update(overrides)
        return Appointment.objects.create(**values)

    def test_doctor_login_redirects_to_doctor_workspace(self):
        response = self.client.post(reverse("signin:login"), {
            "email": "morgan@example.com",
            "password": "DoctorPass!9284",
        })

        self.assertRedirects(response, reverse("doctor-dashboard"))

    def test_doctor_workspace_renders_each_section(self):
        self.client.force_login(self.user)
        for section, title in (
            ("appointments", "Appointments"),
            ("records", "Patient records"),
            ("queue", "Consult queue"),
            ("availability", "Availability"),
        ):
            with self.subTest(section=section):
                response = self.client.get(
                    reverse("doctor-dashboard"),
                    {"section": section},
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, title)
                self.assertContains(response, "doctors/css/portal.css")

    def test_doctor_can_accept_matching_pending_request(self):
        appointment = self.create_appointment()
        self.client.force_login(self.user)

        queue_response = self.client.get(
            reverse("doctor-dashboard"),
            {"section": "queue"},
        )
        self.assertContains(queue_response, "Taylor Patient")

        response = self.client.post(
            reverse("doctor-accept-appointment", args=[appointment.pk])
        )

        self.assertRedirects(
            response,
            f"{reverse('doctor-dashboard')}?section=queue",
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CONFIRMED)
        self.assertEqual(appointment.doctor_name, "Dr. Morgan Lee")

        appointments_response = self.client.get(
            reverse("doctor-dashboard"),
            {"section": "appointments"},
        )
        self.assertContains(appointments_response, "Taylor Patient")

    def test_doctor_queue_only_shows_matching_hospital_and_specialty_requests(self):
        self.create_appointment()
        self.create_appointment(specialization="Neurology")
        self.create_appointment(hospital_name="Other Hospital")
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("doctor-dashboard"),
            {"section": "queue"},
        )

        self.assertContains(response, "Taylor Patient", count=1)
        self.assertEqual(response.context["queue"].count(), 1)

    def test_doctor_can_save_weekly_availability(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("doctor-dashboard") + "?section=availability",
            {
                "availability-TOTAL_FORMS": "1",
                "availability-INITIAL_FORMS": "0",
                "availability-MIN_NUM_FORMS": "0",
                "availability-MAX_NUM_FORMS": "1000",
                "availability-0-day": "MONDAY",
                "availability-0-start_time": "09:00",
                "availability-0-end_time": "17:00",
                "availability-0-slot_duration": "30",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('doctor-dashboard')}?section=availability",
        )
        availability = Availability.objects.get(doctor=self.doctor)
        self.assertEqual(availability.day, "MONDAY")
        self.assertEqual(availability.start_time, time(9, 0))
        self.assertEqual(availability.end_time, time(17, 0))
