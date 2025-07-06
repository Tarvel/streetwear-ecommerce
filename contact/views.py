from django.shortcuts import render
from .models import ContactSubmission
from django.contrib import messages


def contact(request):
    page = "home"
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        contact_submission = ContactSubmission.objects.create(
            name=name,
            email=email,
            message=message,
        )
        messages.info(request, "Your message has been sent.")
    return render(request, "contact/contact.html", {"page": page})
