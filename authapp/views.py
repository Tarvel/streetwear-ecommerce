import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import CustomUserCreationForm, UserDetailForm
from .models import UserDetail

User = get_user_model()


def register(request):
    # if request.user.is_authenticated:
    #     return redirect("home")
    username = str(uuid.uuid4())

    if request.method == "POST":
        user_form = CustomUserCreationForm(request.POST)
        detail_form = UserDetailForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.username = user.email
            user.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("home")
    else:
        user_form = CustomUserCreationForm()
        # detail_form = UserDetailForm()
        # UserDetail.objects.create(
        #     user=user,
        #     phone_number=detail_form.cleaned_data["phone_number"],
        #     address=detail_form.cleaned_data["address"],
        # )

    context = {
        "user_form": user_form,
        "username": username,
    }
    return render(request, "authapp/register.html", context)


def loginPage(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.filter(email=email).first()
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect("login")

        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Incorrect password.")
            return redirect("login")

    return render(request, "authapp/login.html")


def logoutPage(request):
    logout(request)
    return redirect("home")
