from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DepenseViewSet, DepenseFinaleViewSet

# Créer le routeur DRF
router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissement')
router.register(r'depenses', DepenseViewSet, basename='depense')
router.register(r'depenses-finales', DepenseFinaleViewSet, basename='depense_finale')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
