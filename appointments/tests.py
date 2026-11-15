from django.test import TestCase
from django.urls import reverse


class AppointmentStepFlowTests(TestCase):
    def test_review_step_next_redirects_to_home(self):
        response = self.client.post(reverse("appointments:step5"))

        self.assertRedirects(response, reverse("home:home"))
