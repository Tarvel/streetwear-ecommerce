from django.urls import path
from . import views


urlpatterns = [
    path("", views.events, name="events"),
    path('<str:event_slug>/', views.event_detail, name='event_detail'),
]
