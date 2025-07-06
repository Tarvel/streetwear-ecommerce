import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import CustomUserCreationForm, UserDetailForm, UserForm
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
            messages.success(request, f"Welcome to Wimer, {request.user.first_name} 🎉. ")
            return redirect("home")
    else:
        user_form = CustomUserCreationForm()

    context = {
        "user_form": user_form,
        "username": username,
    }
    return render(request, "accounts/register.html", context)


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
            next_url = request.POST.get("next") or "home"
            return redirect(next_url)
        else:
            messages.error(request, "Incorrect password.")
            return redirect("login")

    return render(request, "accounts/login.html")


def logoutPage(request):
    logout(request)
    return redirect("home")


def updatePage(request):
    user = request.user
    UserDetail.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        detail_form = UserDetailForm(request.POST, instance=user.userdetail)

        if user_form.is_valid() and detail_form.is_valid():
            user_form.save()
            detail_form.save()
            messages.info(request, "Details updated")
            return redirect('update_detail')
    else:
        user_form = UserForm(instance=user)
        detail_form = UserDetailForm(instance=user.userdetail)

    return render(request, "accounts/update_detail.html", {"detail_form": detail_form, "user_form": user_form})
