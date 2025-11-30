from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    ProfilCoordinateur,
    DossierDecaissement,
    HistoriqueValidation,
    StatistiquesValidation,
    ModeleDecision,
    AlerteDecaissement,
    Vue_DemandesPendantes
)
from .serializers import (
    ProfilCoordinateurSerializer,
    DossierDecaissementSerializer,
    HistoriqueValidationSerializer,
    StatistiquesValidationSerializer,
    ModeleDecisionSerializer,
    AlerteDecaissementSerializer,
    VueDemandesPendantesSerializer
)

# ============================================================
# ProfilCoordinateur ViewSet
# ============================================================
class ProfilCoordinateurViewSet(viewsets.ModelViewSet):
    queryset = ProfilCoordinateur.objects.all()
    serializer_class = ProfilCoordinateurSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'peut_valider_decaissement']
    search_fields = ['nom_complet', 'email']
    ordering_fields = ['date_embauche', 'nom_complet']
    ordering = ['nom_complet']

# ============================================================
# DossierDecaissement ViewSet
# ============================================================
class DossierDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DossierDecaissement.objects.select_related('coordinateur').prefetch_related('historique_validations', 'alertes')
    serializer_class = DossierDecaissementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priorite', 'type_decaissement', 'coordinateur']
    search_fields = ['numero', 'type_decaissement', 'justification']
    ordering_fields = ['date_reception', 'montant_demande']
    ordering = ['-date_reception']

# ============================================================
# HistoriqueValidation ViewSet
# ============================================================
class HistoriqueValidationViewSet(viewsets.ModelViewSet):
    queryset = HistoriqueValidation.objects.select_related('coordinateur', 'dossier_decaissement')
    serializer_class = HistoriqueValidationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'coordinateur', 'dossier_decaissement']
    search_fields = ['commentaire', 'raison_rejet']
    ordering_fields = ['date_validation']
    ordering = ['-date_validation']

# ============================================================
# StatistiquesValidation ViewSet
# ============================================================
class StatistiquesValidationViewSet(viewsets.ModelViewSet):
    queryset = StatistiquesValidation.objects.select_related('coordinateur')
    serializer_class = StatistiquesValidationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['mois', 'annee', 'coordinateur']
    ordering_fields = ['annee', 'mois']
    ordering = ['-annee', '-mois']

# ============================================================
# ModeleDecision ViewSet
# ============================================================
class ModeleDecisionViewSet(viewsets.ModelViewSet):
    queryset = ModeleDecision.objects.all()
    serializer_class = ModeleDecisionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['est_actif']
    search_fields = ['nom', 'description']
    ordering_fields = ['nom']
    ordering = ['nom']

# ============================================================
# AlerteDecaissement ViewSet
# ============================================================
class AlerteDecaissementViewSet(viewsets.ModelViewSet):
    queryset = AlerteDecaissement.objects.select_related('dossier_decaissement')
    serializer_class = AlerteDecaissementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_alerte', 'severite', 'est_lue']
    search_fields = ['message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def marquer_comme_lue(self, request, pk=None):
        alerte = self.get_object()
        alerte.marquer_comme_lue()
        return Response({'status': 'alerte marquée comme lue'})

# ============================================================
# VueDemandesPendantes ViewSet (read-only)
# ============================================================
class VueDemandesPendantesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vue_DemandesPendantes.objects.all()
    serializer_class = VueDemandesPendantesSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['coordinateur_nom', 'type_decaissement', 'priorite']
    search_fields = ['dossier_numero', 'demande_numero']
    ordering_fields = ['date_reception', 'jours_restants']
    ordering = ['-date_reception']
