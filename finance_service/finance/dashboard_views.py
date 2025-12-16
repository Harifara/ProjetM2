from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementSerializer, DepenseSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_finance(request):
    """
    Dashboard Finance
    - KPI : demandes de décaissement, montants totaux, décaissements effectués
    - Listes : dernières demandes, dernières dépenses
    """
    today = timezone.now().date()

    # ------------------
    # KPI principaux
    # ------------------
    kpi = {
        "total_decaissements": DemandeDecaissement.objects.count(),
        "decaissements_brouillon": DemandeDecaissement.objects.filter(statut='brouillon').count(),
        "decaissements_en_attente": DemandeDecaissement.objects.filter(statut='en_attente_coordonnateur').count(),
        "decaissements_approuve": DemandeDecaissement.objects.filter(statut='approuve').count(),
        "decaissements_rejete": DemandeDecaissement.objects.filter(statut='rejete').count(),
        "decaissements_effectues": DemandeDecaissement.objects.filter(statut='decaisse').count(),
        "montant_total_decaisse": DemandeDecaissement.objects.aggregate(total=Sum("montant_total"))["total"] or 0,
        "montant_total_depense": Depense.objects.aggregate(total=Sum("montant"))["total"] or 0,
    }

    # ------------------
    # Listes récentes (10 dernières)
    # ------------------
    lists = {
        "decaissements": DemandeDecaissementSerializer(
            DemandeDecaissement.objects.order_by("-date_creation")[:10],
            many=True
        ).data,
        "depenses": DepenseSerializer(
            Depense.objects.order_by("-date_depense")[:10],
            many=True
        ).data,
    }

    # ------------------
    # Charts simplifiés (optionnel)
    # ------------------
    charts = {
        "decaissements_par_statut": list(
            DemandeDecaissement.objects.values("statut").annotate(total=Count("id"))
        ),
        "depenses_par_mode": list(
            Depense.objects.values("mode_paiement").annotate(total=Count("id"))
        ),
    }

    return Response({
        "kpi": kpi,
        "lists": lists,
        "charts": charts,
    })
