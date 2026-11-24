from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .forms import DoctorSearchForm
from .models import Availability, Doctor


def _page_url(request, page_number):
    query = request.GET.copy()
    query["page"] = page_number
    return f"?{query.urlencode()}"


def doctor_list(request):
    form = DoctorSearchForm(request.GET or None)
    doctors = (Doctor.objects
               .select_related("user", "hospital")
               .prefetch_related("availability_set")
               .order_by("user__last_name", "user__first_name"))
    searched = False

    if form.is_valid():
        q = form.cleaned_data["q"].strip()
        specialty = form.cleaned_data["specialty"].strip()

        if q:
            doctors = doctors.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(specialization__icontains=q) |
                Q(hospital__name__icontains=q)
            )
        if specialty:
            specialty_filters = [specialty]
            if specialty.lower() in {"ob-gyn", "ob-gyn ec", "obgyne"}:
                specialty_filters = ["OB-Gyne", "OB-Gyn"]
            doctors = doctors.filter(
                Q(specialization__icontains=specialty_filters[0])
                if len(specialty_filters) == 1
                else (
                    Q(specialization__icontains=specialty_filters[0])
                    | Q(specialization__icontains=specialty_filters[1])
                )
            )
        searched = bool(q or specialty)

    paginator = Paginator(doctors, 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_links = [
        {
            "number": page_number,
            "url": _page_url(request, page_number),
            "is_ellipsis": False,
        }
        if isinstance(page_number, int)
        else {"is_ellipsis": True}
        for page_number in paginator.get_elided_page_range(
            page_obj.number,
            on_each_side=1,
            on_ends=1,
        )
    ]

    return render(request, "doctors/list.html",
                  {
                      "form": form,
                      "doctors": page_obj.object_list,
                      "searched": searched,
                      "page_obj": page_obj,
                      "page_links": page_links,
                      "previous_page_url": (
                          _page_url(request, page_obj.previous_page_number())
                          if page_obj.has_previous()
                          else None
                      ),
                      "next_page_url": (
                          _page_url(request, page_obj.next_page_number())
                          if page_obj.has_next()
                          else None
                      ),
                  })


def doctor_profile(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.select_related("user", "hospital").prefetch_related(
            "availability_set"
        ),
        pk=pk,
    )
    return render(request, "doctors/profile.html", {"doctor": doctor})