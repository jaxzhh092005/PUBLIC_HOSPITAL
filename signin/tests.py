import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
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

    def test_signin_without_next_redirects_to_authenticated_home(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )

        response = self.client.post(reverse("signin:login"), {
            "email": "user@example.com",
            "password": "secret123",
        }, follow=True)

        self.assertRedirects(response, reverse("home:home"))
        self.assertContains(response, "Schedule Your Appointment")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_signin_returns_to_safe_next_url(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )
        next_url = f'{reverse("doctors:list")}?specialty=Cardiology'

        response = self.client.post(reverse("signin:login"), {
            "email": "user@example.com",
            "password": "secret123",
            "next": next_url,
        })

        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_signup_preserves_destination_through_login(self):
        next_url = f'{reverse("doctors:list")}?specialty=Cardiology'

        signup_page = self.client.get(
            reverse("signin:signup"),
            {"next": next_url},
        )
        self.assertContains(signup_page, 'name="next"')
        self.assertContains(signup_page, "Log in</a>")

        response = self.client.post(reverse("signin:signup"), {
            "first_name": "Test",
            "last_name": "Patient",
            "email": "new-patient@example.com",
            "password": "secret123",
            "next": next_url,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            f'{reverse("signin:login")}?next=%2Fdoctors%2F%3Fspecialty%3DCardiology',
        )

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

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_forgot_password_sends_reset_link_for_existing_user(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )
        client = Client(enforce_csrf_checks=True)
        url = reverse("signin:forgot_password")
        get_response = client.get(url)
        token_match = re.search(
            rb'name="csrfmiddlewaretoken" value="([^"]+)"',
            get_response.content,
        )
        if token_match is None:
            self.fail("Forgot-password form did not render a CSRF token.")

        response = client.post(
            url,
            {
                "csrfmiddlewaretoken": token_match.group(1).decode(),
                "email": "user@example.com",
            },
        )

        self.assertContains(response, "If an account exists for that email")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["user@example.com"])
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_forgot_password_does_not_reveal_unknown_email(self):
        response = self.client.post(
            reverse("signin:forgot_password"),
            {"email": "missing@example.com"},
        )

        self.assertContains(response, "If an account exists for that email")
        self.assertEqual(len(mail.outbox), 0)
