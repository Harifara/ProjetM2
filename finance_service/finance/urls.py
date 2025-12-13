from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandeDecaissementViewSet, DepenseViewSet, DemandesDisponiblesView

# Créer le router
router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissement')
router.register(r'depenses', DepenseViewSet, basename='depense')

# URL patterns
urlpatterns = [
    # Routes automatiques du router
    path('', include(router.urls)),
    
    # Route spécifique pour récupérer les demandes disponibles (RH + Stock)
    path('demandes-disponibles/', DemandesDisponiblesView.as_view(), name='demandes-disponibles'),
]
