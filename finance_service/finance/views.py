# finance/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import DemandeDecaissement, Depense
from .serializers import (
    DemandeDecaissementCreateSerializer,
    DemandeDecaissementListSerializer,
    DemandeDecaissementDetailSerializer,
    DepenseSerializer,
)

import requests
from django.conf import settings


# ==============================
# ViewSet pour les décaissements
# ==============================
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return DemandeDecaissementListSerializer
        elif self.action == 'retrieve':
            return DemandeDecaissementDetailSerializer
        return DemandeDecaissementCreateSerializer

    # 🔹 Soumettre un décaissement au coordonnateur
    @action(detail=True, methods=['post'])
    def soumettre(self, request, pk=None):
        decaissement = self.get_object()
        try:
            decaissement.soumettre_coordonnateur()
            return Response({"message": "Soumis au coordonnateur"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =====================================
# API pour appliquer la décision coord.
# =====================================
class DecisionDecaissementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, decaissement_id):
        decaissement = get_object_or_404(DemandeDecaissement, id=decaissement_id)
        decision = request.data.get("decision")
        try:
            decaissement.appliquer_decision_coordonnateur(decision)
            return Response({"statut": decaissement.statut}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============================
# ViewSet pour les dépenses
# ============================
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        decaissement = serializer.validated_data['decaissement']
        if decaissement.statut != 'approuve':
            raise ValidationError("Décaissement non approuvé")
        serializer.save()


# =========================================
# API pour récupérer les demandes disponibles
# =========================================
class DemandesDisponiblesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 🔹 Récupérer toutes les demandes déjà utilisées
        decaissements = DemandeDecaissement.objects.exclude(statut='rejete')
        used_rh_ids = set(id for d in decaissements for id in d.demandes_rh_ids)
        used_stock_ids = set(id for d in decaissements for id in d.demandes_stock_ids)

        # 🔹 Appel vers les services RH et Stock
        rh_demandes, stock_demandes = [], []

        try:
            resp_rh = requests.get(f"{settings.RH_SERVICE_URL}/api/demandes/", timeout=5)
            resp_rh.raise_for_status()
            rh_demandes = resp_rh.json()
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes RH: {e}")

        try:
            resp_stock = requests.get(f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/", timeout=5)
            resp_stock.raise_for_status()
            stock_demandes = resp_stock.json()
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes Stock: {e}")

        # 🔹 Filtrer celles déjà utilisées
        rh_dispo = [d for d in rh_demandes if d["id"] not in used_rh_ids]
        stock_dispo = [d for d in stock_demandes if d["id"] not in used_stock_ids]

        return Response({"rh": rh_dispo, "stock": stock_dispo})
