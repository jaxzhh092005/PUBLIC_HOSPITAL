from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import AccountForm, EmailChangeForm, MobileChangeForm
from .models import Profile


def _profile(user):
    return Profile.objects.get_or_create(user=user)[0]


def _show(request, *, mobile_form=None, email_form=None, open_dialog=""):
    return render(request, "accounts/account.html", {
        "editing": False,
        "profile": _profile(request.user),
        "mobile_form": mobile_form or MobileChangeForm(user=request.user),
        "email_form": email_form or EmailChangeForm(user=request.user),
        "open_dialog": open_dialog,  # re-opens the dialog that has errors
    })


@login_required(login_url="signin:login")
def account_detail(request):
    return _show(request)


@login_required(login_url="signin:login")
def account_edit(request):
    user, profile = request.user, _profile(request.user)
    return_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER", "")
    )
    if not url_has_allowed_host_and_scheme(
        return_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return_url = reverse("accounts:detail")

    initial = {
        "first_name": user.first_name,
        "middle_name": profile.middle_name,
        "last_name": user.last_name,
        "birthdate": profile.birthdate,
    }
    form = AccountForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        if form.has_changed():
            data = form.cleaned_data
            user.first_name, user.last_name = data["first_name"], data["last_name"]
            user.save(update_fields=["first_name", "last_name"])
            profile.middle_name, profile.birthdate = data["middle_name"], data["birthdate"]
            profile.save(update_fields=["middle_name", "birthdate"])
            messages.success(request, "Your account was updated.")
        return redirect(return_url)

    return render(request, "accounts/account.html", {
        "editing": True,
        "form": form,
        "return_url": return_url,
    })


@login_required(login_url="signin:login")
@require_POST
def change_mobile(request):
    form = MobileChangeForm(request.POST, user=request.user)
    if form.is_valid():
        profile = _profile(request.user)
        profile.mobile_number = form.cleaned_data["mobile"]
        profile.save(update_fields=["mobile_number"])
        messages.success(request, "Mobile number updated.")
        return redirect("accounts:detail")
    return _show(request, mobile_form=form, open_dialog="mobileDialog")


@login_required(login_url="signin:login")
@require_POST
def change_email(request):
    form = EmailChangeForm(request.POST, user=request.user)
    if form.is_valid():
        request.user.email = form.cleaned_data["email"]
        request.user.save(update_fields=["email"])
        messages.success(request, "Email updated.")
        return redirect("accounts:detail")
    return _show(request, email_form=form, open_dialog="emailDialog")
