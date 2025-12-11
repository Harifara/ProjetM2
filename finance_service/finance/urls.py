from django.urls import path
from .views import (
    DemandeDecaissementListCreateView,
    DemandeDecaissementDetailUpdateView,
    DecaissementValidationView,
    DecaissementRejetView,
    DepenseListView,
    DepenseByDecaissementView
)

app_name = "finance"

urlpatterns = [

    # =====================================================
    # 1️⃣ DÉCAISSEMENTS (Finance) — LISTE / CRÉATION / MODIF
    # =====================================================
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

    # =====================================================
    # 2️⃣ VALIDATION / REJET (Coordinateur)
    # =====================================================
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

    # =====================================================
    # 3️⃣ DÉPENSES — LISTE / FILTRAGE PAR DÉCAISSEMENT
    # =====================================================
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
