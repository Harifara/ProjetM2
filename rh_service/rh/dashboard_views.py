from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# tes imports models et serializers
from .models import Employer, Conge, Contrat, Affectation, Demande, Achat, Payement
from .serializers import EmployerSerializer, CongeSerializer, ContratSerializer, AffectationSerializer, DemandeSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_rh(request):
    user = request.user
    today = timezone.now().date()

    # 🔐 Vérification permissions adaptée à KongJWTUser
    user_roles = getattr(user, "roles", [])  # ou user.groupes
    if "RH" not in user_roles:
        return Response({"detail": "Accès refusé"}, status=403)

    # ==============================
    # KPI
    # ==============================
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

    # ==============================
    # Charts et listes (inchangés)
    # ==============================
    # ... ton code charts et listes ...

    return Response({"kpi": kpi, "charts": charts, "lists": lists})
