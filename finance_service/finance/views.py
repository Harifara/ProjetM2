from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import DemandeDecaissement, DemandeDecaissementItem, Depense
from .serializers import DemandeDecaissementSerializer, DemandeDecaissementItemSerializer, DepenseSerializer

# ----------------------------
# Décaissements
# ----------------------------
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer

# ----------------------------
# Items de décaissement
# ----------------------------
class DemandeDecaissementItemViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissementItem.objects.all()
    serializer_class = DemandeDecaissementItemSerializer

# ----------------------------
# Dépenses
# ----------------------------
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer

# ----------------------------
# Update status d'un item
# ----------------------------
class DemandeDecaissementItemUpdateStatusView(APIView):
    def post(self, request, item_id):
        item = get_object_or_404(DemandeDecaissementItem, id=item_id)
        statut = request.data.get("statut")
        if statut not in ["en_attente", "valide", "rejete"]:
            return Response({"error": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)
        item.statut = statut
        item.save()  # le signal mettra à jour le décaissement et crée la dépense si besoin
        return Response({"success": True, "id": str(item.id), "statut": item.statut})
