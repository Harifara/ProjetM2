# coordonateur/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ValidationCoordinateurViewSet, DemandesCoordoViewSet

router = DefaultRouter()
router.register(r'demandes', DemandesCoordoViewSet, basename='coordo-demande')
router.register(r'validations', ValidationCoordinateurViewSet, basename='coordo-validation')

urlpatterns = [
    path('', include(router.urls)),
]
