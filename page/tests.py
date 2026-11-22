from django.test import TestCase
from django.urls import reverse


class LandingPageTests(TestCase):
    def test_view_more_doctors_control_and_extra_doctor_are_rendered(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="toggleDoctors" type="button"')
        self.assertContains(response, 'aria-controls="moreDoctors" aria-expanded="false"')
        self.assertContains(response, '<li class="doc" id="moreDoctors" hidden style="display: none;">')
        self.assertContains(response, 'moreDoctors.style.display = showMore ? "grid" : "none";')
        self.assertContains(response, "Dr Andrea Santos")
        self.assertContains(response, "SHOW FEWER DOCTORS")
