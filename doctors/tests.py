from datetime import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
