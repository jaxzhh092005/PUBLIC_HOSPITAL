from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SigninPageTests(TestCase):
    def test_auth_pages_render(self):
        for route_name in (
            "signin:login",
            "signin:signup",
            "signin:forgot_password",
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "/static/signin/css/auth.css")
                self.assertContains(response, "/static/signin/images/logo.png")
                self.assertContains(response, "/static/signin/images/campus.png")

    def test_homepage_signin_link_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("signin:login"))

    def test_signin_without_next_redirects_to_home(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )

        response = self.client.post(reverse("signin:login"), {
            "email": "user@example.com",
            "password": "secret123",
        })

        self.assertRedirects(response, reverse("landing"))

    def test_invalid_email_formats_show_an_error(self):
        requests = (
            (
                "signin:login",
                {"email": "not-an-email", "password": "test"},
            ),
            (
                "signin:signup",
                {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "not-an-email",
                    "password": "test",
                },
            ),
            ("signin:forgot_password", {"email": "not-an-email"}),
        )
        for route_name, data in requests:
            with self.subTest(route_name=route_name):
                response = self.client.post(reverse(route_name), data)
                self.assertContains(response, "Please enter a valid email address.")
