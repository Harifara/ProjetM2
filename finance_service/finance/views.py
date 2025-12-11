from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementSerializer, DepenseSerializer

# -----------------------------
# ViewSet pour DemandeDecaissement
# -----------------------------
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all().order_by('-date_creation')
    serializer_class = DemandeDecaissementSerializer

    # -----------------------------
    # Créer un décaissement
    # -----------------------------
    def perform_create(self, serializer):
        """
        Remplit automatiquement 'created_by' avec l'utilisateur connecté.
        """
        serializer.save(created_by=self.request.user.id)

    # -----------------------------
    # Validation / rejet par coordo
    # -----------------------------
    @action(detail=True, methods=['post'])
    def coordo_validation(self, request, pk=None):
        """
        Endpoint appelé par le service coordonnateur pour valider/rejeter une demande.
        URL: POST /decaissements/{id}/coordo_validation/
        """
        try:
            demande = self.get_object()
        except DemandeDecaissement.DoesNotExist:
            return Response({'detail': 'Demande non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        decision = request.data.get('decision')
        coordo_id = request.data.get('coordo_id')
        commentaire = request.data.get('commentaire', '')

        if decision not in ['valide', 'rejete']:
            return Response({'detail': 'Decision invalide'}, status=status.HTTP_400_BAD_REQUEST)

        demande.coordo_decision = decision
        demande.coordo_id = coordo_id
        demande.coordo_commentaire = commentaire
        demande.coordo_date = timezone.now()
        demande.envoyee = True
        demande.save(update_fields=[
            'coordo_decision', 'coordo_id', 'coordo_commentaire', 'coordo_date', 'envoyee'
        ])

        serializer = DemandeDecaissementSerializer(demande)
        return Response(serializer.data, status=status.HTTP_200_OK)
# -----------------------------
# ViewSet pour Depense
# -----------------------------
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all().order_by('-date_creation')
    serializer_class = DepenseSerializer
