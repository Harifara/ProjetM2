from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DemandeDecaissementItemViewSet, DepenseViewSet

# ----------------------------
# Création du router
# ----------------------------
router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissement')
router.register(r'items', DemandeDecaissementItemViewSet, basename='decaissement-item')
router.register(r'depenses', DepenseViewSet, basename='depense')

# ----------------------------
# Inclusion des routes
# ----------------------------
urlpatterns = [
    path('', include(router.urls)),
]
