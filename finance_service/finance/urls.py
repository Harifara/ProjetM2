# finance/urls.py

from django.urls import path
from .views import (
    DemandeDecaissementListCreateView,
    DemandeDecaissementDetailUpdateView,
    DecaissementValidationView,
    DecaissementRejetView,
    DepenseListView,
    DepenseByDecaissementView
)

urlpatterns = [

    # --------------------
    #  DÉCAISSEMENTS (Finance)
    # --------------------
    path(
        "decaissements/",
        DemandeDecaissementListCreateView.as_view(),
        name="decaissement-list-create"
    ),

    path(
        "decaissements/<uuid:id>/",
        DemandeDecaissementDetailUpdateView.as_view(),
        name="decaissement-detail-update"
    ),

    # --------------------
    #  VALIDATION (Coordinateur)
    # --------------------
    path(
        "decaissements/<uuid:id>/valider/",
        DecaissementValidationView.as_view(),
        name="decaissement-valider"
    ),

    path(
        "decaissements/<uuid:id>/rejeter/",
        DecaissementRejetView.as_view(),
        name="decaissement-rejeter"
    ),

    # --------------------
    #  DÉPENSES
    # --------------------
    path(
        "depenses/",
        DepenseListView.as_view(),
        name="depense-list"
    ),

    path(
        "decaissements/<uuid:id>/depenses/",
        DepenseByDecaissementView.as_view(),
        name="depense-by-decaissement"
    ),
]
