from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DemandeDecaissement, DemandeDecaissementItem, Depense
from .serializers import (
    DemandeDecaissementSerializer,
    DemandeDecaissementItemSerializer,
    DepenseSerializer
)

# ----------------------------
# ViewSet pour les décaissements
# ----------------------------
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer

    def perform_create(self, serializer):
        # Crée le décaissement
        decaissement = serializer.save()
        items_data = self.request.data.get('items', [])
        for item_data in items_data:
            DemandeDecaissementItem.objects.create(
                decaissement=decaissement,
                **item_data
            )
        decaissement.calculer_total()
        decaissement.mettre_a_jour_statut()

# ----------------------------
# ViewSet pour les items de décaissement
# ----------------------------
class DemandeDecaissementItemViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissementItem.objects.all()
    serializer_class = DemandeDecaissementItemSerializer

    def perform_create(self, serializer):
        item = serializer.save()
        # Met à jour le décaissement parent
        item.decaissement.calculer_total()
        item.decaissement.mettre_a_jour_statut()

# ----------------------------
# ViewSet pour les dépenses
# ----------------------------
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer

# ----------------------------
# API pour mettre à jour le statut d’un item (coordinateur)
# ----------------------------
class DemandeDecaissementItemUpdateStatusView(APIView):
    """
    Endpoint pour mettre à jour le statut d'un item de décaissement.
    Exemple de payload: {"statut": "valide"}
    """
    def post(self, request, item_id):
        try:
            item = DemandeDecaissementItem.objects.get(id=item_id)
        except DemandeDecaissementItem.DoesNotExist:
            return Response({"detail": "Item non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        statut = request.data.get('statut')
        if statut not in ['en_attente', 'valide', 'rejete']:
            return Response({"detail": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)

        item.statut = statut
        item.save()
        # Le signal post_save gérera la création de la dépense si nécessaire
        return Response(DemandeDecaissementItemSerializer(item).data)
