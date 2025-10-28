from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from coordinateur.views import health_view 

schema_view = get_schema_view(
    openapi.Info(
        title="Coordinateur Service API",
        default_version='v1',
        description="Service coordinateur pour la validation des demandes de décaissement",
        contact=openapi.Contact(email="admin@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/coordinateur/health/', health_view, name='health'),
    path('api/coordinateur/', include('coordinateur.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
