from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("home:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Schedule Your Appointment")
        self.assertContains(response, "/static/css/base.css")
        self.assertContains(response, "/static/home/css/home.css")

    def test_next_saves_appointment_type_and_opens_step_one(self):
        response = self.client.post(
            reverse("home:home"),
            {"appointment_type": "clinical"},
        )

        self.assertRedirects(response, reverse("appointments:step1"))
        self.assertEqual(self.client.session["appointment_type"], "clinical")

        step_response = self.client.get(response.url)
        self.assertEqual(step_response.status_code, 200)
        self.assertContains(step_response, "Specialization")
        self.assertContains(step_response, 'name="specialization"')
        self.assertContains(step_response, "appointments/css/appointments.css")
        self.assertContains(step_response, 'aria-label="Booking progress"')
