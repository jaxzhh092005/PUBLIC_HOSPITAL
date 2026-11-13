
from django.urls import path
from . import views

app_name = "signin"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
]
