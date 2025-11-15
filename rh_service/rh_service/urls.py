from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API RH
    path("api/rh/", include("rh.urls")),
]

# Sert les fichiers médias uniquement en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
