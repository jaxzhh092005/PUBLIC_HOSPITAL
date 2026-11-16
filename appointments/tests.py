from django.test import TestCase
from django.urls import reverse


class AppointmentStepFlowTests(TestCase):
    def test_review_step_without_session_redirects_to_first_missing_step(self):
        response = self.client.post(reverse("appointments:step5"))

        self.assertRedirects(response, reverse("appointments:step1"))
