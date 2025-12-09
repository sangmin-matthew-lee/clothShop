from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages

from .models import Account


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("/shopping")
        messages.error(request, "Invalid email or password.")
    return render(request, "shopping/login.html")


def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "shopping/register.html")

        try:
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.phone = phone
            user.is_active = True
            user.save()
            messages.success(request, "Account created. Please log in.")
            return redirect("/shopping/login")
        except Exception:
            messages.error(request, "Could not create account. Please check details.")
    return render(request, "shopping/register.html")


def logout_view(request):
    auth_logout(request)
    return redirect("/shopping")
