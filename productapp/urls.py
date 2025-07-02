from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("", views.search, name="search"),
    path("shops/", views.shop, name="shop"),
    path("shops/<str:drop>/", views.shopDrops, name="shop_drop"),
    path("shop/<str:slug>/", views.product_detail, name="product_detail"),
    path('cart/add/<int:pk>/', views.addToCart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.updateCart, name='update_cart'),
    path('cart/', views.cartPage, name="cart"),
    # path('events/', views.events, name='events'),
    # path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    # path('gallery/', views.gallery, name='gallery'),
    # path('about/', views.about, name='info'),
    # path('contact/', views.contact, name='contact'),
]
