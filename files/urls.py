from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("", views.file_list, name="list"),
    path("<int:pk>/download/", views.download_file, name="download"),
]
