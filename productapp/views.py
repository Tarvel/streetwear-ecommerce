import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseNotFound
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import (
    Product,
    ProductVariant,
    CartItem,
    Drop,
    ContactSubmission,
    GalleryImage,
    Event,
    ProductImage,
)


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
    return render(request, "productapp/contact.html", {"page": page})


def about(request):
    return render(request, "productapp/about.html")


def events(request):
    upcoming_events = Event.objects.all()
    context = {"upcoming_events": upcoming_events}
    return render(request, "productapp/events.html", context)


def home(request):
    slideshow_images = list(Product.objects.all())
    random.shuffle(slideshow_images)
    newest_products = Product.objects.filter(is_available=True).order_by("-created_at")[
        0:8
    ]
    context = {
        "slideshow_images": slideshow_images,
        "newest_products": newest_products,
    }
    return render(request, "productapp/index.html", context)


def shop(request):
    sort = request.GET.get("sort") if request.GET.get("sort") is not None else ""
    products_list = Product.objects.all().order_by("-created_at")
    q = request.GET.get("q")
    if q:
        products_list = Product.objects.filter(name__icontains=q).order_by(
            "-created_at"
        )

    if sort == " ":
        products_list = Product.objects.all().order_by("-created_at")
    elif sort == "low-high":
        products_list = Product.objects.all().order_by("base_price")
    elif sort == "high-low":
        products_list = Product.objects.all().order_by("-base_price")

    elif sort == "newest":
        products_list = Product.objects.all().order_by("-created_at")
    elif sort == "oldest":
        products_list = Product.objects.all().order_by("created_at")

    paginator = Paginator(products_list, 8)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "products": products,
    }
    return render(request, "productapp/shop.html", context)


def shopDrops(request, drop):
    page = drop
    selected_drop = Drop.objects.get(name=drop)
    product_drop = Product.objects.filter(drop=selected_drop)
    sort = request.GET.get("sort") if request.GET.get("sort") is not None else ""

    if sort == "":
        products_list = product_drop
    elif sort == "low-high":
        products_list = product_drop.order_by("price")
    elif sort == "high-low":
        products_list = product_drop.order_by("-price")

    elif sort == "newest":
        products_list = product_drop.order_by("-created_at")
    elif sort == "oldest":
        products_list = product_drop.order_by("created_at")

    paginator = Paginator(products_list, 8)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "products": products,
        "page": page,
    }
    return render(request, "productapp/shop.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("variants", "additional_images"), slug=slug
    )
    variants = product.variants.all()
    selected_variant = None
    variant_id_str = request.GET.get("variant")

    if variant_id_str:
        selected_variant = next(
            (v for v in variants if str(v.id) == variant_id_str), None
        )
        if not selected_variant:
            messages.warning(request, "The selected option is no longer available.")
            return redirect("product_detail", slug=slug)

    if not selected_variant and variants:
        selected_variant = variants[0]

    cart_item = None
    if request.user.is_authenticated and selected_variant:
        cart_item = CartItem.objects.filter(
            user=request.user, variant=selected_variant
        ).first()

    context = {
        "product": product,
        "variants": variants,
        "selected_variant": selected_variant,
        "cart": cart_item,
    }
    return render(request, "productapp/product_detail.html", context)


@login_required(login_url="login")
def cartPage(request):
    cart_items = CartItem.objects.filter(user=request.user).all()

    context = {
        "cart_items": cart_items,
    }

    return render(request, "productapp/cart.html", context)


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
        cart = CartItem.objects.create(
            user=request.user,
            quantity=quantity,
            total_price=total_price,
            variant=variant,
        )
        messages.info(
            request, f"Product{'s' if quantity > 1 else ''} added to your cart."
        )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def updateCart(request, variant_id):
    try:
        variant = ProductVariant.objects.filter(pk=variant_id)
    except ProductVariant.DoesNotExist:
        messages.error(request, "Product does not exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    try:
        cart = CartItem.objects.filter(user=request.user, variant__id=variant_id)
    except CartItem.DoesNotExist:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        quantity = (
            request.POST.get("quantity")
            if request.POST.get("quantity") is not None
            else 1
        )
        print(quantity)
        variant_price = ProductVariant.objects.get(pk=variant_id)
        new_total_price = int(variant_price.price) * int(quantity)
        cart.update(quantity=quantity, total_price=new_total_price)
        messages.info(
            request,
            f"Cart updated: {quantity} product{'s' if int(quantity) > 1 else ''} added.",
        )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def removeCart(request, cart_id):
    try:
        cart = CartItem.objects.filter(pk=cart_id).first()
    except CartItem.DoesNotExist:
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
