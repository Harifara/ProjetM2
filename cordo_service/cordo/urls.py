from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfilCoordinateurViewSet,
    DossierDecaissementViewSet,
    HistoriqueValidationViewSet,
    StatistiquesValidationViewSet,
    ModeleDecisionViewSet,
    AlerteDecaissementViewSet,
    VueDemandesPendantesViewSet
)

# Création du routeur DRF
router = DefaultRouter()
router.register(r'profil-coordinateur', ProfilCoordinateurViewSet, basename='profil-coordinateur')
router.register(r'dossier-decaissement', DossierDecaissementViewSet, basename='dossier-decaissement')
router.register(r'historique-validation', HistoriqueValidationViewSet, basename='historique-validation')
router.register(r'statistiques-validation', StatistiquesValidationViewSet, basename='statistiques-validation')
router.register(r'modele-decision', ModeleDecisionViewSet, basename='modele-decision')
router.register(r'alerte-decaissement', AlerteDecaissementViewSet, basename='alerte-decaissement')
router.register(r'demandes-pendantes', VueDemandesPendantesViewSet, basename='demandes-pendantes')

# URLs finales
urlpatterns = [
    path('', include(router.urls)),
]
