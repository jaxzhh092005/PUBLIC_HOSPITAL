from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountURLTests(TestCase):
    def test_account_edit_route_requires_authentication(self):
        response = self.client.get(reverse("accounts:edit"))
        login_url = f"{reverse('signin:login')}?next={reverse('accounts:edit')}"

        self.assertRedirects(
            response,
            login_url,
            fetch_redirect_response=False,
        )
        self.assertContains(self.client.get(login_url), f'name="next" value="{reverse("accounts:edit")}"')

    def test_settings_nav_link_targets_account_overview(self):
        response = self.client.get(reverse("home:home"))

        self.assertContains(response, f'href="{reverse("accounts:detail")}" class="nav-settings"')

    def test_account_edit_cancel_returns_to_previous_page(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:edit"))

        self.assertContains(response, 'aria-label="Cancel" onclick="if (history.length > 1) { history.back(); return false; }"')

    def test_account_edit_save_returns_to_previous_page(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )
        self.client.force_login(user)
        previous_page = f"http://testserver{reverse('home:home')}"

        response = self.client.get(
            reverse("accounts:edit"),
            HTTP_REFERER=previous_page,
        )
        self.assertContains(response, f'name="next" value="{previous_page}"')

        response = self.client.post(reverse("accounts:edit"), {
            "first_name": "Updated",
            "middle_name": "",
            "last_name": "User",
            "birthdate": "",
            "next": previous_page,
        }, follow=True)

        self.assertRedirects(response, previous_page)
        self.assertContains(response, "Your account was updated.")
        self.assertContains(response, 'class="flash" role="status"')

    def test_account_edit_unchanged_data_does_not_show_success_message(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
            first_name="Same",
            last_name="User",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("accounts:edit"), {
            "first_name": "Same",
            "middle_name": "",
            "last_name": "User",
            "birthdate": "",
            "next": reverse("accounts:detail"),
        }, follow=True)

        self.assertRedirects(response, reverse("accounts:detail"))
        self.assertNotContains(response, "Your account was updated.")
        self.assertNotContains(response, 'class="flash" role="status"')

    def test_account_edit_save_rejects_external_return_url(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )
        self.client.force_login(user)

        response = self.client.post(reverse("accounts:edit"), {
            "first_name": "Updated",
            "middle_name": "",
            "last_name": "User",
            "birthdate": "",
            "next": "https://example.com/",
        })

        self.assertRedirects(response, reverse("accounts:detail"))

    def test_signin_returns_to_account_settings(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="secret123",
        )

        response = self.client.post(reverse("signin:login"), {
            "email": "user@example.com",
            "password": "secret123",
            "next": reverse("accounts:detail"),
            "remember": "on",
        })

        self.assertRedirects(response, reverse("accounts:detail"))
        self.assertContains(
            self.client.get(reverse("accounts:detail")),
            f'href="{reverse("accounts:edit")}" class="acc-icon" aria-label="Edit account"',
        )


class AdminAccessTests(TestCase):
    def test_superuser_can_manage_registered_project_models(self):
        admin_user = get_user_model().objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="secret123",
        )
        self.client.force_login(admin_user)

        for app_label in ("accounts", "appointments", "doctors", "files", "hospitals", "nurse", "patients"):
            for model in apps.get_app_config(app_label).get_models():
                with self.subTest(model=model.__name__):
                    self.assertTrue(admin.site.is_registered(model))
                    url = reverse(f"admin:{app_label}_{model._meta.model_name}_changelist")
                    self.assertEqual(self.client.get(url).status_code, 200)
