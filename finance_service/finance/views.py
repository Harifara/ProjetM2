from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementSerializer, DepenseSerializer
import requests
from django.conf import settings


class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les demandes de décaissement.
    """
    queryset = DemandeDecaissement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DemandeDecaissementSerializer

    def get_queryset(self):
        """
        Filtre les demandes non encore décaisées si on est dans la liste "demandes reçues".
        """
        queryset = super().get_queryset()
        en_reception = self.request.query_params.get("en_reception")
        if en_reception == "true":
            queryset = queryset.exclude(statut="decaisse")
        return queryset

    @action(detail=True, methods=["post"])
    def soumettre(self, request, pk=None):
        """
        Soumettre un décaissement au coordonnateur.
        """
        decaissement = self.get_object()
        try:
            decaissement.soumettre_coordonnateur()
            # 🔹 Mettre à jour le statut des demandes associées
            for rh_id in decaissement.demandes_rh_ids:
                requests.patch(f"{settings.RH_SERVICE_URL}/api/rh/demandes/{rh_id}/", json={"status": "en_decaissement"})
            for stock_id in decaissement.demandes_stock_ids:
                requests.patch(f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/{stock_id}/", json={"statut": "en_decaissement"})
            return Response(
                {"message": "Décaissement soumis au coordonnateur"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def appliquer_decision(self, request, pk=None):
        """
        Appliquer la décision du coordonnateur.
        """
        decaissement = self.get_object()
        decision = request.data.get("decision")
        try:
            decaissement.appliquer_decision_coordonnateur(decision)

            # 🔹 Si validé, mettre à jour le statut des demandes RH et Stock
            if decision == "valide":
                for rh_id in decaissement.demandes_rh_ids:
                    requests.patch(f"{settings.RH_SERVICE_URL}/api/rh/demandes/{rh_id}/", json={"status": "valide"})
                for stock_id in decaissement.demandes_stock_ids:
                    requests.patch(f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/{stock_id}/", json={"statut": "valide"})

            return Response({"statut": decaissement.statut}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def demandes_disponibles(self, request):
        """
        Retourne toutes les demandes RH et Stock disponibles pour créer un décaissement.
        """
        rh_demandes = []
        stock_demandes = []

        # 🔹 RH
        try:
            resp = requests.get(f"{settings.RH_SERVICE_URL}/api/rh/demandes/", timeout=5)
            resp.raise_for_status()
            all_rh = resp.json()
            # On ne prend que les demandes en attente
            rh_demandes = [d for d in all_rh if d.get("status") == "en_attente"]
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes RH: {e}")

        # 🔹 Stock
        try:
            resp = requests.get(f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/", timeout=5)
            resp.raise_for_status()
            all_stock = resp.json()
            stock_demandes = [d for d in all_stock if d.get("statut") == "en_attente"]
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes Stock: {e}")

        return Response({"rh": rh_demandes, "stock": stock_demandes})


class DepenseViewSet(viewsets.ModelViewSet):
    """
    Gestion des dépenses liées à un décaissement.
    """
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        decaissement = serializer.validated_data["decaissement"]
        if decaissement.statut != "approuve":
            raise ValidationError("Décaissement non approuvé")
        serializer.save()
