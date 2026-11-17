from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from patients.models import Patient
from .models import MedicalFile


class FileAccessTests(TestCase):
    def create_patient(self, username):
        user = get_user_model().objects.create_user(username=username, password="test")
        return Patient.objects.create(
            user=user,
            birthdate=date(1990, 1, 1),
            gender="Prefer not to say",
            mobile="09123456789",
            address="Main Street",
            emergency_contact="Contact",
        )

    def test_files_page_opens_without_redirecting(self):
        response = self.client.get(reverse("files:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Files")
        self.assertContains(response, "Files from your doctors or lab tests will go here.")

    def test_patient_files_page_renders(self):
        patient = self.create_patient("patient")
        self.client.force_login(patient.user)

        response = self.client.get(reverse("files:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/static/files/css/files.css")
        self.assertContains(response, 'class="files-sidebar"')
        self.assertNotContains(response, 'class="files-menu"')
        self.assertContains(response, "All Files")
        self.assertContains(response, "Prescription")
        self.assertContains(response, "Lab Tests")
        self.assertContains(response, "Files from your doctors or lab tests will go here.")

    def test_patient_cannot_download_another_patients_file(self):
        patient = self.create_patient("patient")
        other_patient = self.create_patient("other")
        medical_file = MedicalFile.objects.create(
            patient=other_patient,
            file_type="LAB",
            document="medical_files/private.pdf",
        )
        self.client.force_login(patient.user)

        response = self.client.get(reverse("files:download", args=[medical_file.pk]))

        self.assertEqual(response.status_code, 404)
