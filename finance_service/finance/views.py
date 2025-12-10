from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementSerializer, DepenseSerializer
from django.db.models import Q

# ===========================
# ViewSet pour DemandeDecaissement
# ===========================
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all().order_by('-date_creation')
    serializer_class = DemandeDecaissementSerializer

    def get_queryset(self):
        """
        Filtrer selon source_service si nécessaire,
        et trier par date_creation décroissante.
        """
        qs = super().get_queryset()
        source_service = self.request.query_params.get('source_service')
        if source_service:
            qs = qs.filter(source_service=source_service)
        return qs

    def create(self, request, *args, **kwargs):
        """
        Créer une demande de décaissement et lier les dépenses
        non encore envoyées du service correspondant.
        """
        source_service = request.data.get('source_service')
        created_by = request.data.get('created_by')  # UUID de l'utilisateur

        if not source_service or not created_by:
            return Response(
                {"error": "source_service et created_by sont requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Créer la demande
        demande = DemandeDecaissement.objects.create(
            source_service=source_service,
            created_by=created_by,
            total_montant=0,
            envoyee=True  # la demande est maintenant envoyée
        )

        # Récupérer les dépenses du service qui ne sont pas encore envoyées
        depenses_non_envoyees = Depense.objects.filter(
            demande__isnull=True,
            description__icontains=source_service  # optionnel selon ton flux
        )

        # Lier les dépenses à cette demande
        for depense in depenses_non_envoyees:
            depense.demande = demande
            depense.save()

        # Calculer le total automatiquement
        demande.calculer_total()

        serializer = self.get_serializer(demande)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """
        Valider toutes les dépenses de la demande
        """
        demande = self.get_object()
        depenses = demande.depenses.all()
        for dep in depenses:
            dep.statut = 'valide'
            dep.save()
        demande.calculer_total()
        serializer = self.get_serializer(demande)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def rejeter(self, request, pk=None):
        """
        Rejeter toutes les dépenses de la demande
        """
        commentaire = request.data.get('commentaire', '')
        demande = self.get_object()
        depenses = demande.depenses.all()
        for dep in depenses:
            dep.statut = 'rejete'
            dep.save()
            if commentaire:
                dep.description += f" (Rejet: {commentaire})"
        demande.calculer_total()
        serializer = self.get_serializer(demande)
        return Response(serializer.data)
