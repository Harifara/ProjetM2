from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DistrictViewSet, CommuneViewSet, FokontanyViewSet,
    FonctionViewSet, AffectationViewSet, EmployerViewSet,
    CongeViewSet, TypeCongeViewSet, TypeContratViewSet, ContratViewSet,
    LocationViewSet, ElectriciteViewSet,
    ModePayementViewSet, DemandeViewSet, PayementViewSet,
    TypeAchatViewSet, AchatViewSet
)

router = DefaultRouter()

router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'communes', CommuneViewSet, basename='commune')
router.register(r'fokontanys', FokontanyViewSet, basename='fokontany')
router.register(r'fonctions', FonctionViewSet, basename='fonction')
router.register(r'affectations', AffectationViewSet, basename='affectation')
router.register(r'employers', EmployerViewSet, basename='employer')
router.register(r'conges', CongeViewSet, basename='conge')
router.register(r'type-conges', TypeCongeViewSet, basename='type-conge')  # <-- ajouté
router.register(r'type-contrats', TypeContratViewSet, basename='type-contrat')
router.register(r'contrats', ContratViewSet, basename='contrat')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'electricites', ElectriciteViewSet, basename='electricite')
router.register(r'mode-payements', ModePayementViewSet, basename='mode-payement')
router.register(r'demandes', DemandeViewSet, basename='demande')
router.register(r'payements', PayementViewSet, basename='payement')
router.register(r'type-achats', TypeAchatViewSet, basename='type-achat')
router.register(r'achats', AchatViewSet, basename='achat')

urlpatterns = [
    path('', include(router.urls)),
]
