from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render

from .models import MedicalFile


def file_list(request):
    files = MedicalFile.objects.none()
    if request.user.is_authenticated:
        files = MedicalFile.objects.filter(patient__user=request.user)
    query = request.GET.get("q", "").strip()
    file_type = request.GET.get("type", "")

    if query:
        files = files.filter(Q(file_type__icontains=query) | Q(document__icontains=query))
    if file_type in dict(MedicalFile.FILE_TYPES):
        files = files.filter(file_type=file_type)

    return render(request, "files/list.html", {
        "files": files.order_by("-uploaded_at"),
        "q": query,
        "file_type": file_type,
    })


@login_required(login_url="signin:login")
def download_file(request, pk):
    medical_file = get_object_or_404(
        MedicalFile,
        pk=pk,
        patient__user=request.user,
    )
    file_handle = default_storage.open(medical_file.document.name, "rb")
    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=Path(medical_file.document.name).name,
    )
