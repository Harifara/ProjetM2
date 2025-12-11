# finance/urls.py
from django.urls import path
from .views import (
    DemandeDecaissementListCreateView,
    DemandeDecaissementDetailUpdateView,
    DemandeEnvoyerCoordoView,
    DemandeValiderCoordoView,
    DemandeRejeterCoordoView,
    DepenseCreateView,
    DepenseValidationView,
    DepenseRejetView,
)

urlpatterns = [
    path("decaissements/", DemandeDecaissementListCreateView.as_view(), name="decaissement-list-create"),
    path("decaissements/<uuid:id>/", DemandeDecaissementDetailUpdateView.as_view(), name="decaissement-detail-update"),
    path("decaissements/<uuid:id>/envoyer/", DemandeEnvoyerCoordoView.as_view(), name="decaissement-envoyer-coordo"),
    path("decaissements/<uuid:id>/valider-coordo/", DemandeValiderCoordoView.as_view(), name="decaissement-valider-coordo"),
    path("decaissements/<uuid:id>/rejeter-coordo/", DemandeRejeterCoordoView.as_view(), name="decaissement-rejeter-coordo"),

    # Depenses
    path("depenses/", DepenseCreateView.as_view(), name="depense-create"),
    path("depenses/<uuid:depense_id>/valider/", DepenseValidationView.as_view(), name="depense-valider"),
    path("depenses/<uuid:depense_id>/rejeter/", DepenseRejetView.as_view(), name="depense-rejeter"),
]
