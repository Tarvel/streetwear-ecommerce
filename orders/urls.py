from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.orderHistory, name="order-history"),
    path("<str:order_id>/", views.orderDetail, name="order-detail"),
]