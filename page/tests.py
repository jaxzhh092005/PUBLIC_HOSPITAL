from django.test import TestCase
from django.urls import reverse


class LandingPageTests(TestCase):
    def test_view_more_doctors_control_and_extra_doctor_are_rendered(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<a class="logo" href="{reverse("landing")}"')
        self.assertContains(response, 'id="toggleDoctors" type="button"')
        self.assertContains(response, 'aria-controls="moreDoctors" aria-expanded="false"')
        self.assertContains(response, '<li class="doc" id="moreDoctors" hidden>')
        self.assertContains(response, "Dr Andrea Santos")
        self.assertContains(response, "SHOW FEWER DOCTORS")

    def test_specialty_cards_link_to_public_doctor_list_with_mapped_specialty(self):
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

    def test_specialty_dropdown_links_to_public_doctor_specialty_filters(self):
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
        self.assertContains(
            response,
            'window.location.href = "{}?"'.format(reverse("doctors:list")),
        )

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
