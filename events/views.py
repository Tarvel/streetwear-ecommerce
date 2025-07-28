from django.shortcuts import render, get_object_or_404
from .models import Event
from django.utils import timezone


def events(request):
    print(request.user.username)
    upcoming_events = Event.objects.filter(date__gt=timezone.now())
    past_events = Event.objects.filter(date__lt=timezone.now())

    context = {
        "upcoming_events": upcoming_events,
        "past_events": past_events,
    }
    return render(request, "events/events.html", context)


def event_detail(request, event_slug):
    upcoming = Event.objects.filter(slug=event_slug, date__gt=timezone.now())
    event = get_object_or_404(Event, slug=event_slug)

    context = {
        "event": event,
        "upcoming": upcoming,
    }
    return render(request, "events/event_detail.html", context)
