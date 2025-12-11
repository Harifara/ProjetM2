from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import DemandeDecaissement, Depense, DepenseFinale
from .serializers import DemandeDecaissementSerializer, DepenseSerializer, DepenseFinaleSerializer
from django.db.models import Q

# ===========================
# ViewSet pour DemandeDecaissement
# ===========================
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all().order_by('-date_creation')
    serializer_class = DemandeDecaissementSerializer

    def get_queryset(self):
        """Filtrer par source_service si passé en query param"""
        qs = super().get_queryset()
        source_service = self.request.query_params.get('source_service')
        if source_service:
            qs = qs.filter(source_service=source_service)
        return qs

    def create(self, request, *args, **kwargs):
        """
        Crée une demande de décaissement par le service finance.
        Les dépenses liées sont encore en attente jusqu'à validation coordo.
        """
        source_service = request.data.get('source_service')
        created_by = request.data.get('created_by')

        if not source_service or not created_by:
            return Response(
                {"error": "source_service et created_by sont requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        demande = DemandeDecaissement.objects.create(
            source_service=source_service,
            created_by=created_by,
            total_montant=0,
            envoyee=True  # La demande est envoyée au coordonnateur
        )

        serializer = self.get_serializer(demande)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """
        Valider toutes les dépenses d'une demande par le coordonnateur.
        Une fois validées, elles deviennent des DepenseFinale.
        """
        demande = self.get_object()
        depenses = demande.depenses.all()
        for dep in depenses:
            dep.statut = 'valide'
            dep.save()  # Le signal créera automatiquement DepenseFinale
        demande.calculer_total()
        serializer = self.get_serializer(demande)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def rejeter(self, request, pk=None):
        """
        Rejeter toutes les dépenses d'une demande par le coordonnateur.
        """
        commentaire = request.data.get('commentaire', '')
        demande = self.get_object()
        depenses = demande.depenses.all()
        for dep in depenses:
            dep.statut = 'rejete'
            if commentaire:
                dep.description += f" (Rejet: {commentaire})"
            dep.save()
        demande.calculer_total()
        serializer = self.get_serializer(demande)
        return Response(serializer.data)


# ===========================
# ViewSet pour Depense (optionnel)
# ===========================
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all().order_by('-date_creation')
    serializer_class = DepenseSerializer


# ===========================
# ViewSet pour DepenseFinale (lecture seule)
# ===========================
class DepenseFinaleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DepenseFinale.objects.all().order_by('-date_creation')
    serializer_class = DepenseFinaleSerializer
