from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from patients.models import Patient


class PatientDashboardTests(TestCase):
    def test_patient_dashboard_requires_login(self):
        response = self.client.get(reverse('patients:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/signin/?next=/patients/')

    def test_patient_dashboard_renders_for_logged_in_patient(self):
        user = get_user_model().objects.create_user(
            username='patient1',
            email='patient1@example.com',
            password='secret123',
        )
        Patient.objects.create(
            user=user,
            birthdate='1990-01-15',
            gender='Female',
            mobile='09123456789',
            address='123 Main Street',
            emergency_contact='Maria Doe',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('patients:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient Dashboard')
