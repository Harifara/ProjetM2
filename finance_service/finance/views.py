from rest_framework import viewsets, status
from rest_framework.response import Response
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


