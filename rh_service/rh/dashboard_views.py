from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from .models import Employer, Conge, Contrat, Affectation, Demande, Achat, Payement
from .serializers import EmployerSerializer, CongeSerializer, ContratSerializer, AffectationSerializer, DemandeSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_rh(request):
    """
    Dashboard RH simplifié à la manière du dashboard Stock
    - KPI : employés, congés, contrats, affectations, demandes, finance
    - Listes : derniers employés, congés, contrats, affectations, demandes
    """
    today = timezone.now().date()
    user = request.user

    # ------------------
    # KPI principaux
    # ------------------
    kpi = {
        "total_employes": Employer.objects.count(),
        "employes_actifs": Employer.objects.filter(status_employer="actif").count(),
        "employes_conge": Employer.objects.filter(status_employer="conge").count(),
        "employes_inactifs": Employer.objects.filter(status_employer="inactif").count(),
        "employes_suspendus": Employer.objects.filter(status_employer="suspendu").count(),

        "conges_en_attente": Conge.objects.filter(status_conge="en_attente").count(),
        "conges_en_cours": Conge.objects.filter(status_conge="approuve", date_debut__lte=today, date_fin__gte=today).count(),
        "conges_refuses": Conge.objects.filter(status_conge="refuse").count(),

        "contrats_actifs": Contrat.objects.filter(status_contrat="actif").count(),
        "contrats_expires": Contrat.objects.filter(status_contrat="expire").count(),
        "contrats_expirant_30j": Contrat.objects.filter(status_contrat="actif", date_fin_contrat__lte=today + timedelta(days=30)).count(),

        "affectations_actives": Affectation.objects.filter(status_affectation="active").count(),

        "demandes_total": Demande.objects.count(),
        "demandes_en_attente": Demande.objects.filter(status="en_attente").count(),
        "demandes_validees": Demande.objects.filter(status="valide").count(),
        "demandes_refusees": Demande.objects.filter(status="refuse").count(),

        "montant_achats": Achat.objects.aggregate(total=Sum("montant"))["total"] or 0,
        "montant_payements": Payement.objects.filter(montant__isnull=False).aggregate(total=Sum("montant"))["total"] or 0,
    }

    # ------------------
    # Listes récentes (10 derniers)
    # ------------------
    lists = {
        "employes": EmployerSerializer(
            Employer.objects.select_related("fonction", "district").order_by("-created_at")[:10],
            many=True
        ).data,
        "conges": CongeSerializer(
            Conge.objects.select_related("employer", "type_conge").order_by("-date_creation")[:10],
            many=True
        ).data,
        "contrats": ContratSerializer(
            Contrat.objects.select_related("employer").order_by("-created_at")[:10],
            many=True
        ).data,
        "affectations": AffectationSerializer(
            Affectation.objects.select_related("employer", "nouveau_fonction", "nouveau_district").order_by("-date_creation_affectation")[:10],
            many=True
        ).data,
        "demandes": DemandeSerializer(
            Demande.objects.prefetch_related("achats", "payements").order_by("-date_demande")[:10],
            many=True
        ).data,
    }

    # ------------------
    # Charts simplifiés (optionnel)
    # ------------------
    charts = {
        "employes_par_statut": list(
            Employer.objects.values("status_employer").annotate(total=Count("id"))
        ),
        "conges_par_statut": list(
            Conge.objects.values("status_conge").annotate(total=Count("id"))
        ),
        "contrats_par_nature": list(
            Contrat.objects.values("nature_contrat").annotate(total=Count("id"))
        ),
        "demandes_par_statut": list(
            Demande.objects.values("status").annotate(total=Count("id"))
        ),
    }

    return Response({
        "kpi": kpi,
        "lists": lists,
        "charts": charts,
    })
