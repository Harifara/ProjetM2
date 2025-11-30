from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TypeDecaissementViewSet,
    DemandeDecaissementViewSet,
    DepenseViewSet,
    BulletinPaieViewSet,
    ValidationDemandeViewSet
)

# Création du router DRF
router = DefaultRouter()
router.register(r'types-decaissement', TypeDecaissementViewSet, basename='type-decaissement')
router.register(r'demandes-decaissement', DemandeDecaissementViewSet, basename='demande-decaissement')
router.register(r'depenses', DepenseViewSet, basename='depense')
router.register(r'bulletins-paie', BulletinPaieViewSet, basename='bulletin-paie')
router.register(r'validations-demandes', ValidationDemandeViewSet, basename='validation-demande')

# URLs finales
urlpatterns = [
    path('', include(router.urls)),
]
