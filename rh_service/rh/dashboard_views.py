from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from .models import (
    Employer, Conge, Contrat, Affectation,
    Fonction, District, Demande, Achat, Payement
)
from .serializers import (
    EmployerSerializer, CongeSerializer, ContratSerializer,
    AffectationSerializer, DemandeSerializer,
    FonctionSerializer, DistrictSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_rh(request):
    user = request.user
    today = timezone.now().date()

    # 🔐 Sécurité
    if not (user.is_superuser or user.groups.filter(name__iexact='RH').exists()):
        return Response({"detail": "Accès refusé"}, status=403)

    # =====================================================
    # 📊 KPI PRINCIPAUX (CARDS)
    # =====================================================
    kpi = {
        # Employés
        "total_employes": Employer.objects.count(),
        "employes_actifs": Employer.objects.filter(status_employer='actif').count(),
        "employes_conge": Employer.objects.filter(status_employer='conge').count(),
        "employes_inactifs": Employer.objects.filter(status_employer='inactif').count(),
        "employes_suspendus": Employer.objects.filter(status_employer='suspendu').count(),

        # Congés
        "conges_en_attente": Conge.objects.filter(status_conge='en_attente').count(),
        "conges_en_cours": Conge.objects.filter(
            status_conge='approuve',
            date_debut__lte=today,
            date_fin__gte=today
        ).count(),
        "conges_refuses": Conge.objects.filter(status_conge='refuse').count(),

        # Contrats
        "contrats_actifs": Contrat.objects.filter(status_contrat='actif').count(),
        "contrats_expires": Contrat.objects.filter(status_contrat='expire').count(),
        "contrats_expirant_30j": Contrat.objects.filter(
            status_contrat='actif',
            date_fin_contrat__lte=today + timezone.timedelta(days=30)
        ).count(),

        # Affectations
        "affectations_actives": Affectation.objects.filter(status_affectation='active').count(),

        # Finance
        "demandes_total": Demande.objects.count(),
        "demandes_en_attente": Demande.objects.filter(status='en_attente').count(),
        "demandes_validees": Demande.objects.filter(status='valide').count(),
        "demandes_refusees": Demande.objects.filter(status='refuse').count(),

        "montant_achats": Achat.objects.aggregate(total=Sum('montant'))['total'] or 0,
        "montant_payements": Payement.objects.aggregate(total=Sum('montant'))['total'] or 0,
    }

    # =====================================================
    # 📈 CHARTS – RÉPARTITIONS
    # =====================================================

    # Employés par sexe
    employes_par_sexe = list(
        Employer.objects.values('sexe')
        .annotate(total=Count('id'))
    )

    # Employés par statut
    employes_par_statut = list(
        Employer.objects.values('status_employer')
        .annotate(total=Count('id'))
    )

    # Employés par fonction
    employes_par_fonction = list(
        Employer.objects.values('fonction__nom_fonction')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Employés par district
    employes_par_district = list(
        Employer.objects.values('district__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Congés par statut
    conges_par_statut = list(
        Conge.objects.values('status_conge')
        .annotate(total=Count('id'))
    )

    # Contrats par nature
    contrats_par_nature = list(
        Contrat.objects.values('nature_contrat')
        .annotate(total=Count('id'))
    )

    # Demandes par statut
    demandes_par_statut = list(
        Demande.objects.values('status')
        .annotate(total=Count('id'))
    )

    # =====================================================
    # 📆 CHARTS TEMPORELS (LINE / BAR)
    # =====================================================

    # Entrées RH par mois
    employes_par_mois = list(
        Employer.objects.annotate(
            mois=TruncMonth('date_entree')
        ).values('mois')
        .annotate(total=Count('id'))
        .order_by('mois')
    )

    # Congés par mois
    conges_par_mois = list(
        Conge.objects.annotate(
            mois=TruncMonth('date_creation')
        ).values('mois')
        .annotate(total=Count('id'))
        .order_by('mois')
    )

    # Montants payés par mois
    payements_par_mois = list(
        Payement.objects.annotate(
            mois=TruncMonth('date_payement')
        ).values('mois')
        .annotate(total=Sum('montant'))
        .order_by('mois')
    )

    # =====================================================
    # 📋 LISTES RÉCENTES
    # =====================================================
    employes = Employer.objects.select_related('fonction', 'district').order_by('-created_at')[:10]
    conges = Conge.objects.select_related('employer', 'type_conge').order_by('-date_creation')[:10]
    contrats = Contrat.objects.select_related('employer').order_by('-created_at')[:10]
    affectations = Affectation.objects.select_related(
        'employer', 'nouveau_fonction', 'nouveau_district'
    ).order_by('-date_creation_affectation')[:10]
    demandes = Demande.objects.prefetch_related('achats', 'payements').order_by('-date_demande')[:10]

    # =====================================================
    # 📤 RESPONSE FINALE
    # =====================================================
    return Response({
        "kpi": kpi,

        "charts": {
            "employes_par_sexe": employes_par_sexe,
            "employes_par_statut": employes_par_statut,
            "employes_par_fonction": employes_par_fonction,
            "employes_par_district": employes_par_district,
            "conges_par_statut": conges_par_statut,
            "contrats_par_nature": contrats_par_nature,
            "demandes_par_statut": demandes_par_statut,

            "employes_par_mois": employes_par_mois,
            "conges_par_mois": conges_par_mois,
            "payements_par_mois": payements_par_mois,
        },

        "lists": {
            "employes": EmployerSerializer(employes, many=True).data,
            "conges": CongeSerializer(conges, many=True).data,
            "contrats": ContratSerializer(contrats, many=True).data,
            "affectations": AffectationSerializer(affectations, many=True).data,
            "demandes": DemandeSerializer(demandes, many=True).data,
        }
    })
