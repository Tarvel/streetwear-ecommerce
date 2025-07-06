from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from .models import Cart
from products.models import ProductVariant
from django.template.loader import render_to_string


@login_required(login_url="login")
def cartPage(request):
    cart_items = Cart.objects.filter(user=request.user).all()
    cart_subtotal = sum(item.total_price for item in cart_items)

    context = {
        "cart_items": cart_items,
        "cart_subtotal": cart_subtotal,
    }

    return render(request, "cart/cart.html", context)


@login_required(login_url="login")
def addToCart(request, variant_id):
    variant = ProductVariant.objects.filter(pk=variant_id).first()
    if not variant:
        messages.error(request, "Product does not exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1
        total_price = int(variant.price) * int(quantity)
        cart = Cart.objects.create(
            user=request.user,
            quantity=quantity,
            total_price=total_price,
            variant=variant,
        )
        messages.info(request, "Added to cart")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def updateCartShop(request, variant_id):
    try:
        variant = ProductVariant.objects.filter(pk=variant_id)
    except ProductVariant.DoesNotExist:
        messages.error(request, "Product does not exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    try:
        cart = Cart.objects.filter(user=request.user, variant__id=variant_id)
    except Cart.DoesNotExist:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        quantity = (
            request.POST.get("quantity")
            if request.POST.get("quantity") is not None
            else 1
        )
        variant_price = ProductVariant.objects.get(pk=variant_id)
        new_total_price = int(variant_price.price) * int(quantity)
        cart.update(quantity=quantity, total_price=new_total_price)
        messages.info(
            request,
            f"Updated: {quantity} {variant_price.product.name.title()}{'s' if int(quantity) > 1 else ''} in cart.",
        )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def updateCart(request, variant_id):
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return JsonResponse({"error": "Product does not exist."}, status=404)

    cart = Cart.objects.filter(user=request.user, variant__id=variant_id)

    if request.method == "POST":
        quantity = request.POST.get("quantity", 1)
        new_total_price = int(variant.price) * int(quantity)
        cart.update(quantity=quantity, total_price=new_total_price)
        msg = f"Updated: {quantity} {variant.product.name.title()}{'s' if int(quantity) > 1 else ''} in cart."

        cart_items = Cart.objects.filter(user=request.user)
        cart_subtotal = sum(item.total_price for item in cart_items)

        html = render_to_string(
            "cart/_cart_items.html",
            {
                "cart_items": cart_items,
                "cart_subtotal": cart_subtotal,
            },
            request=request,
        )

        return JsonResponse(
            {
                "html": html,
                "message": msg,
            }
        )

    return JsonResponse({"error": "Invalid request."}, status=400)


@login_required(login_url="login")
def removeCart(request, cart_id):
    try:
        cart = Cart.objects.filter(pk=cart_id).first()
    except Cart.DoesNotExist:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        if request.POST.get("remove") == "true":
            messages.info(
                request,
                f"{cart.variant.product.name.title()} [{cart.variant.size.title()}-{cart.variant.colour.title() if cart.variant.size.title() is not None else ""}] has been removed from cart",
            )
            cart.delete()
        else:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
