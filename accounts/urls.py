from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.account_detail, name="detail"),
    path("edit/", views.account_edit, name="edit"),
    path("change-mobile/", views.change_mobile, name="change_mobile"),
    path("change-email/", views.change_email, name="change_email"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
]