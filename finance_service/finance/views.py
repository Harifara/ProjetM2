from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import DemandeDecaissement, DemandeDecaissementItem, Depense
from .serializers import DemandeDecaissementSerializer, DemandeDecaissementItemSerializer, DepenseSerializer

# ------------------------
# ViewSet Décaissement
# ------------------------
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer

    def perform_create(self, serializer):
        # Calcul automatique du total
        decaissement = serializer.save()
        decaissement.calculer_total()

# ------------------------
# ViewSet Item Décaissement
# ------------------------
class DemandeDecaissementItemViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissementItem.objects.all()
    serializer_class = DemandeDecaissementItemSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.statut = request.data.get('statut', instance.statut)
        instance.save()
        # Mise à jour automatique du statut global du décaissement
        instance.decaissement.mettre_a_jour_statut()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# ------------------------
# ViewSet Dépense
# ------------------------
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        statut_paiement = request.data.get('statut_paiement', instance.statut_paiement)
        instance.statut_paiement = statut_paiement
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
