# coordonnateur/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ValidationCoordonnateurViewSet
from .dashboard_views import dashboard_coordonnateur


# Router pour le ViewSet
router = DefaultRouter()
router.register('validations', ValidationCoordonnateurViewSet, basename='validation-coordonnateur')

# URLs finales
urlpatterns = [
    path('', include(router.urls)),  # inclut /validations/
    path('dashboard/', dashboard_coordonnateur, name='dashboard-coordonnateur'),  # nouvel endpoint pour dashboard
]
