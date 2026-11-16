from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("specialization/", views.step1, name="step1"),
    path("date/", views.step2, name="step2"),
    path("information/", views.step3, name="step3"),
    path("documents/", views.step4, name="step4"),
    path("review/", views.step5, name="step5"),
]