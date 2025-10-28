from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

# =====================================================
# 📘 Swagger / OpenAPI Schema
# =====================================================
schema_view = get_schema_view(
    openapi.Info(
        title="Service RH API",
        default_version="v1",
        description=(
            "API du microservice RH — "
            "gestion des employés, contrats, congés, affectations, paiements et achats."
        ),
        contact=openapi.Contact(email="rh@example.com"),
        license=openapi.License(name="Propriété interne © 2025"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# =====================================================
# 🌐 URL Patterns
# =====================================================
urlpatterns = [
    # 🎛️ Interface d’administration Django
    path("admin/", admin.site.urls),

    # 🧩 Endpoints du microservice RH
    path("api/rh/", include("rh.urls")),

    # 📜 Documentation Swagger / ReDoc
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # ✅ Health check global (utile pour Docker monitoring)
    path("health/", lambda request: JsonResponse({"status": "ok", "service": "rh_service"})),
]

# =====================================================
# 🖼️ Fichiers statiques & médias (en mode debug)
# =====================================================
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
