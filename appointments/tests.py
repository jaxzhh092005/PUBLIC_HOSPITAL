from django.test import TestCase
from django.urls import reverse

from .forms import InformationForm


class AppointmentStepFlowTests(TestCase):
    def test_review_step_without_session_redirects_to_first_missing_step(self):
        response = self.client.post(reverse("appointments:step5"))

        self.assertRedirects(response, reverse("appointments:step1"))

    def test_information_form_rejects_non_digits_in_contact_number(self):
        data = {
            "last_name": "User",
            "first_name": "Test",
            "middle_name": "A",
            "suffix": "",
            "birthdate": "2000-01-01",
            "gender": "Male",
            "email": "test@example.com",
            "region": "NCR",
            "province": "N/A",
            "municipality": "Manila",
            "barangay": "Barangay",
            "street": "1 Main Street",
        }

        for number in ("0912345678a", "091234-6789"):
            with self.subTest(number=number):
                form = InformationForm({**data, "contact_number": number})

                self.assertFalse(form.is_valid())
                self.assertIn("contact_number", form.errors)

    def test_information_form_accepts_digits_only_contact_number(self):
        form = InformationForm({
            "last_name": "User",
            "first_name": "Test",
            "middle_name": "A",
            "suffix": "",
            "birthdate": "2000-01-01",
            "gender": "Male",
            "email": "test@example.com",
            "contact_number": "09123456789",
            "region": "NCR",
            "province": "N/A",
            "municipality": "Manila",
            "barangay": "Barangay",
            "street": "1 Main Street",
        })

        self.assertTrue(form.is_valid(), form.errors)
