from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render

User = get_user_model()


def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def login_view(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        if not email:
            error = "Please enter your email address."
        elif not is_valid_email(email):
            error = "Please enter a valid email address."
        else:
            user_obj = User.objects.filter(email__iexact=email).first()
            user = authenticate(request, username=user_obj.username, password=password) if user_obj else None

            if user is not None:
                login(request, user)
                if not request.POST.get("remember"):
                    request.session.set_expiry(0)
                return redirect("/")
            error = "Incorrect email or password."
    return render(request, "signin/login.html", {"error": error})


def signup_view(request):
    error = None
    if request.method == "POST":
        first = request.POST.get("first_name", "").strip()
        last = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not (first and last and email and password):
            error = "Please fill in all fields."
        elif not is_valid_email(email):
            error = "Please enter a valid email address."
        elif User.objects.filter(email__iexact=email).exists():
            error = "An account with this email already exists."
        else:
            User.objects.create_user(
                username=email, email=email, password=password,
                first_name=first, last_name=last,
            )
            return redirect("signin:login")
    return render(request, "signin/signup.html", {"error": error})


def forgot_password_view(request):
    message = None
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            message = "Please enter your email address."
        elif not is_valid_email(email):
            message = "Please enter a valid email address."
        else:
            message = "Password reset email delivery is not configured yet."
    return render(request, "signin/forgot_password.html", {"message": message})
