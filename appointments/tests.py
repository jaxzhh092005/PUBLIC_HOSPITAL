from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import InformationForm


class AppointmentStepFlowTests(TestCase):
    def test_review_step_without_session_redirects_to_first_missing_step(self):
        user = get_user_model().objects.create_user(username="patient")
        self.client.force_login(user)

        response = self.client.post(reverse("appointments:step5"))

        self.assertRedirects(response, reverse("appointments:step1"))

    def test_booking_steps_require_login_and_return_to_requested_step(self):
        for step in ("step1", "step2", "step3", "step4", "step5"):
            with self.subTest(step=step):
                step_url = reverse(f"appointments:{step}")
                response = self.client.get(step_url)

                self.assertRedirects(
                    response,
                    f'{reverse("signin:login")}?next={step_url}',
                    fetch_redirect_response=False,
                )

        review_url = reverse("appointments:step5")
        response = self.client.post(review_url)
        self.assertRedirects(
            response,
            f'{reverse("signin:login")}?next={review_url}',
            fetch_redirect_response=False,
        )

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
