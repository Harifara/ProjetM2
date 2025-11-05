from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

# ==========================================================
# 📘 Swagger / Redoc (Documentation API)
# ==========================================================
schema_view = get_schema_view(
    openapi.Info(
        title="Authentication Service API",
        default_version="v1",
        description=(
            "Service d'authentification centralisée pour la plateforme. "
            "Inclut la gestion des utilisateurs, les journaux d’audit et la sécurité JWT."
        ),
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ==========================================================
# 🌍 Routes principales du projet Django
# ==========================================================
urlpatterns = [
    # 🛠️ Interface d’administration Django
    path("admin/", admin.site.urls),

    # 🔐 Routes du module d’authentification
    path("api/auth/", include("authentication.urls")),
    

    # 📘 Documentation Swagger + Redoc
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    # ✅ Endpoint global de santé (utilisé par Docker / monitoring)
    path("health/", lambda request: JsonResponse({"status": "ok"})),
]
