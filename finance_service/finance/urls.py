from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DemandeDecaissementViewSet,
    DepenseViewSet,
    DecisionDecaissementView,
    DemandesDisponiblesView,
)

router = DefaultRouter()
router.register("decaissements", DemandeDecaissementViewSet, basename="decaissements")
router.register("depenses", DepenseViewSet, basename="depenses")

urlpatterns = [
    path("", include(router.urls)),
    path("decaissements/<uuid:decaissement_id>/decision/", DecisionDecaissementView.as_view(), name="decision-decaissement"),
    path("demandes-disponibles/", DemandesDisponiblesView.as_view(), name="demandes-disponibles"),
]
