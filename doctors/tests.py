from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from hospitals.models import Hospital
from .models import Doctor


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
        Doctor.objects.create(
            user=user,
            hospital=hospital,
            specialization="Cardiology",
            license_number="LIC-001",
        )

        response = self.client.get(reverse("doctors:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Morgan Lee")
        self.assertContains(response, "Cardiology")
        self.assertContains(response, reverse("doctors:list"))
        self.assertContains(response, 'aria-current="page"', count=1)
