from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class LandingPageTests(TestCase):
    def test_online_doctors_section_is_not_rendered(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<a class="logo" href="{reverse("landing")}"')
        self.assertNotContains(response, "Doctors Online Now")
        self.assertNotContains(response, "CONSULT NOW")
        self.assertNotContains(response, "moreDoctors")
        self.assertNotContains(response, "toggleDoctors")

    def test_specialty_cards_link_to_doctor_list_with_mapped_specialty(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(response.status_code, 200)
        doctor_list_url = reverse("doctors:list")
        for specialty in (
            "General%20Medicine",
            "OB-Gyn",
            "Pediatrics",
            "Endocrinology",
            "Eye%20and%20Vision",
            "Cardiology",
            "Dermatology",
            "Pulmonology",
            "Gastroenterology",
            "ENT",
            "Nephrology",
            "Neurology",
        ):
            self.assertContains(
                response,
                f'href="{doctor_list_url}?specialty={specialty}"',
            )
    def test_specialty_dropdown_requires_login_before_searching(self):
        response = self.client.get(reverse("landing"))

        for option in (
            'value="General Medicine"',
            'value="Family Medicine"',
            'value="Neurology"',
            'value="Cardiology"',
            'value="Pediatrics"',
            'value="Skin &amp; Dermatology"',
            'value="Orthopedic Surgery"',
            'value="Eye and Vision"',
            'value="Nephrology"',
        ):
            self.assertContains(response, f"<option {option}")
        self.assertContains(response, f'const doctorListPath = "{reverse("doctors:list")}"')
        self.assertContains(response, f'const loginUrl = "{reverse("signin:login")}"')
        self.assertContains(response, 'document.addEventListener("click"')
        self.assertContains(response, "target.closest('a[href^=\"' + doctorListPath + '\"]')")
        self.assertContains(response, "new URLSearchParams({ next })")
        self.assertContains(response, "const isAuthenticated = false")

    def test_authenticated_specialty_dropdown_skips_login(self):
        user = get_user_model().objects.create_user(username="patient")
        self.client.force_login(user)

        response = self.client.get(reverse("landing"))

        self.assertContains(response, "const isAuthenticated = true")

    def test_common_condition_cards_link_to_related_doctor_specialties(self):
        response = self.client.get(reverse("landing"))
        doctor_list_url = reverse("doctors:list")

        for specialty in (
            "Dermatology",
            "Orthopedic%20Surgery",
            "General%20Medicine",
            "Neurology",
            "Endocrinology",
            "Cardiology",
            "Nephrology",
            "OB-Gyn",
        ):
            self.assertContains(
                response,
                f'href="{doctor_list_url}?specialty={specialty}"',
            )
