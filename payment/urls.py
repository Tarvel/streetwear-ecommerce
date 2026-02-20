from django.urls import path
from . import views

urlpatterns = [
    path("sucess/<str:order_id>/", views.paymentSuccessful, name="payment-success"),
    path("failed/<str:order_id>/", views.paymentFailed, name="payment-fail"),
    path("retry/<str:order_id>/", views.paymentRetry, name="payment-retry"),
    path("status/<str:order_id>/", views.check_payment_status, name="check-payment-status"),
    path('webhook/paystack/', views.paystack_webhook),
]
