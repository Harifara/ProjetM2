from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import DemandeDecaissement, DemandeDecaissementItem, Depense
from .serializers import DemandeDecaissementSerializer, DemandeDecaissementItemSerializer, DepenseSerializer

# ----------------------------
# ViewSet pour les décaissements
# ----------------------------
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer

    @action(detail=True, methods=['post'])
    def calculer_total(self, request, pk=None):
        decaissement = self.get_object()
        decaissement.calculer_total()
        return Response({"total_montant": decaissement.total_montant})

    @action(detail=True, methods=['post'])
    def mettre_a_jour_statut(self, request, pk=None):
        decaissement = self.get_object()
        decaissement.mettre_a_jour_statut()
        return Response({"statut": decaissement.statut})


# ----------------------------
# ViewSet pour les items
# ----------------------------
class DemandeDecaissementItemViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissementItem.objects.all()
    serializer_class = DemandeDecaissementItemSerializer


# ----------------------------
# ViewSet pour les dépenses
# ----------------------------
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
