import json
import uuid
from django.conf import settings
from payment.paystack import checkout
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User
from orders.models import Order
from .models import Payment
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import hmac
import hashlib


@login_required(login_url="login")
def paymentSuccessful(request, order_id):
    if request.user.is_authenticated:
        user = request.user
    else:
        return redirect("login")
    order = Order.objects.get(order_id=order_id)
    order.status = "paid"
    order.updated_at = timezone.now()
    order.save()
    try:
        payment = Payment.objects.get(order__order_id=order_id)
        payment.status = "success"
        payment.paid_at = timezone.now()
        payment.save()
    except Payment.DoesNotExist:
        payment = None
        messages.info(request, "Payment pending")

    context = {
        "order": order,
        "user": user,
    }
    return render(request, "payment/payment_successful.html", context)


@login_required(login_url="login")
def paymentFailed(request, order_id):
    return render(request, "payment/payment_failed.html")


@login_required
def paymentRetry(request, order_id):
    if request.user.is_authenticated:
        user = request.user
    else:
        return redirect("login")
    order = Order.objects.get(order_id=order_id)
    order.reference = f"ord-{uuid.uuid4().hex[0:8]}"
    order.save()

    # convert UUID to string (cos 'Object of type UUID is not JSON serializable' lol)
    json_data = json.dumps({"order_id": str(order.order_id)})

    # Build callback URL
    payment_success_url = reverse(
        "payment-success", kwargs={"order_id": order.order_id}
    )
    callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

    checkout_data = {
        "email": user.email or user.username,
        "amount": int(order.total_amount * 100),  # convert to kobo
        "currency": "NGN",
        "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
        "reference": str(order.reference),
        "callback_url": callback_url,
        "metadata": {
            "order_id": str(order.order_id),
            "user_id": user.id,
            "payment_reference": str(order.reference),
        },
        "label": f"Checkout For order_{order.order_id}",
    }

    # Call checkout logic
    status, checkout_url, payment_reference = checkout(checkout_data)

    payment, create = Payment.objects.get_or_create(
        order=order,
        user=user,
        defaults={
            "amount": order.total_amount,
        },
    )

    if status:
        return redirect(checkout_url)

    else:
        print(payment_reference)
        order.status = "failed"
        order.updated_at = timezone.now()
        order.save()

        payment.status = "failed"
        payment.paid_at = timezone.now()
        payment.save()

        messages.error(request, checkout_url)  # Shows error message
        return redirect("payment-fail", order.order_id)


@csrf_exempt
def paystack_webhook(request):
    print("testing webok")
    secret = settings.PAYSTACK_SECRET_KEY
    request_body = request.body

    hash = hmac.new(secret.encode("utf-8"), request_body, hashlib.sha512).hexdigest()

    if hash == request.META.get("HTTP_X_PAYSTACK_SIGNATURE"):
        webhook_post_data = json.loads(request_body)
        print(f'This is data: {webhook_post_data}')

        if webhook_post_data["event"] == "charge.success":
            metadata = webhook_post_data["data"]["metadata"]

            # get oder_id and user_id to retrive their respective instances, then get payment_reference to populate the newly created Payment instance
            order_id = metadata["order_id"]
            user_id = metadata["user_id"]
            payment_reference = metadata["payment_reference"]
            print(payment_reference)

            # retrive order and user instances then add them to the newly created Payment instance
            order = Order.objects.get(order_id=order_id)
            user = User.objects.get(id=user_id)

            payment = Payment.objects.create(
                order=order,
                user=user,
                payment_reference=payment_reference,
                amount=order.total_amount,
                status="success",
                paid_at=timezone.now(),
            )

    return HttpResponse(status=200)
