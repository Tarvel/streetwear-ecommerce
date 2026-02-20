import json
import uuid
from django.conf import settings
from payment.paystack import checkout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
    order = Order.objects.get(order_id=order_id)
    
    # DO NOT SAVE ANYTHING HERE. Just check status.
    # If the webhook hasn't arrived yet, the user will see "Pending"
    # You can add a frontend HTMX poller to refresh if you want real-time updates.
    
    context = {
        "order": order,
        "user": request.user,
    }
    return render(request, "payment/payment_successful.html", context)


@login_required(login_url="login")
def paymentFailed(request, order_id):
    return render(request, "payment/payment_failed.html")


@login_required
def paymentRetry(request, order_id):
    order = Order.objects.get(order_id=order_id)
    
    # 1. Generate NEW reference for this specific attempt
    new_reference = f"ord-{uuid.uuid4().hex[0:8]}"
    
    # 2. Update Order with new reference (so the webhook knows where to look)
    order.reference = new_reference
    order.save()


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

    # 3. Create NEW Payment intent
    payment = Payment.objects.create(
        order=order,
        user=user,
        payment_reference=new_reference, # Important!
        amount=order.total_amount,
        status="pending"
    )

    # 4. Call Paystack
    status, checkout_url, ref = checkout(checkout_data)

    if status:
        return redirect(checkout_url)
    else:
        # Update THIS payment attempt to failed
        payment.status = "failed"
        payment.save()
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
            # Paystack returns the reference you sent in Step 1
            reference = webhook_post_data["data"]["reference"] 
            
            try:
                # 1. Find the PENDING payment using the reference
                payment = Payment.objects.get(payment_reference=reference)
                
                # 2. Mark Payment as Success
                payment.status = "success"
                payment.paid_at = timezone.now()
                payment.save()
                
                # 3. Mark Order as Paid
                order = payment.order
                order.status = "paid"
                order.updated_at = timezone.now()
                order.save()
                
            except Payment.DoesNotExist:
                pass 

    return HttpResponse(status=200)


@login_required(login_url="login")
def check_payment_status(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        # Get the latest payment for this order
        payment = Payment.objects.filter(order=order).order_by("-created_at").first()
        
        status = payment.status if payment else "pending"
        
        context = {
            "order": order,
            "status": status,
            "payment": payment,
        }
        
        if status == "success":
            return render(request, "payment/partials/_payment_status_success.html", context)
        elif status == "failed":
            return render(request, "payment/partials/_payment_status_failed.html", context)
        else:
            # Still pending, return the polling partial
            return render(request, "payment/partials/_payment_status_pending.html", context)
            
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)

