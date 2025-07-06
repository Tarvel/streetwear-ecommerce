from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("products.urls")),
    path("auth/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
    path("contact-us/", include("contact.urls")),
    path("events/", include("events.urls")),
    path("gallery/", include("gallery.urls")),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
