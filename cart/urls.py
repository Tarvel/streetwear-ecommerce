from django.urls import path
from . import views


urlpatterns = [
    path("add/<int:variant_id>/", views.addToCart, name="add_to_cart"),
    path("update/shop/<int:variant_id>/", views.updateCart, name="update_cart"),
    path("update/<int:variant_id>/", views.updateCartShop, name="update_cart_shop"),
    path("delete/<int:cart_id>/", views.removeCart, name="delete_cart"),
    path("", views.cartPage, name="cart"),
    path("checkout/", views.checkoutPage, name="checkout"),
]
