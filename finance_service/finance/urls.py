from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DemandeDecaissementViewSet,
    DepenseViewSet,
    DemandesDisponiblesView,
    DecisionDecaissementView,
)

# Router DRF
router = DefaultRouter()
router.register(r'decaissements', DemandeDecaissementViewSet, basename='decaissement')
router.register(r'depenses', DepenseViewSet, basename='depense')

urlpatterns = [
    # Routes automatiques (CRUD)
    path('', include(router.urls)),

    # RH + Stock disponibles pour créer un décaissement
    path(
        'demandes-disponibles/',
        DemandesDisponiblesView.as_view(),
        name='demandes-disponibles'
    ),

    # Décision du coordonnateur (APPROUVER / REJETER)
    path(
        'decaissements/<uuid:decaissement_id>/decision/',
        DecisionDecaissementView.as_view(),
        name='decision-decaissement'
    ),
]
