from django.urls import path
from .views import (
    ValidationCoordinateurListView,
    ValidationCoordinateurDetailView,
    ValidationCoordinateurCreateView,
    ValidationByDecaissementView,
)

urlpatterns = [

    # ---------------------------
    # Liste et création
    # ---------------------------
    path(
        "validations/",
        ValidationCoordinateurListView.as_view(),
        name="validation-list"
    ),
    path(
        "validations/create/",
        ValidationCoordinateurCreateView.as_view(),
        name="validation-create"
    ),

    # ---------------------------
    # Détail d'une validation
    # ---------------------------
    path(
        "validations/<uuid:id>/",
        ValidationCoordinateurDetailView.as_view(),
        name="validation-detail"
    ),

    # ---------------------------
    # Lister les validations d'un décaissement
    # ---------------------------
    path(
        "decaissements/<uuid:decaissement_id>/validations/",
        ValidationByDecaissementView.as_view(),
        name="validations-by-decaissement"
    ),
]
