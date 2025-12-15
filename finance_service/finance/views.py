# finance/views.py
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
        Met à jour le statut des demandes associées en "en_decaissement".
        """
        decaissement = self.get_object()
        rh_ids = request.data.get("rh_ids", [])
        stock_ids = request.data.get("stock_ids", [])

        try:
            # 🔹 Mettre les demandes RH en "en_decaissement"
            for rh_id in rh_ids:
                requests.patch(
                    f"{settings.RH_SERVICE_URL}/api/demandes/{rh_id}/",
                    json={"status": "en_decaissement"},
                    timeout=5
                )

            # 🔹 Mettre les demandes Stock en "en_decaissement"
            for stock_id in stock_ids:
                requests.patch(
                    f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/{stock_id}/",
                    json={"statut": "en_decaissement"},
                    timeout=5
                )

            decaissement.soumettre_coordonnateur()
            return Response(
                {"message": "Décaissement soumis au coordonnateur"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response(
                {"error": f"Impossible de mettre à jour les demandes : {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def appliquer_decision(self, request, pk=None):
        """
        Appliquer la décision du coordonnateur.
        Si approuvé, les demandes associées deviennent "valide".
        """
        decaissement = self.get_object()
        decision = request.data.get("decision")
        rh_ids = [d.id for d in decaissement.demandes_rh.all()]
        stock_ids = [d.id for d in decaissement.demandes_stock.all()]

        try:
            decaissement.appliquer_decision_coordonnateur(decision)

            if decision == "approuve":
                # 🔹 Mettre toutes les demandes associées en "valide"
                for rh_id in rh_ids:
                    requests.patch(
                        f"{settings.RH_SERVICE_URL}/api/demandes/{rh_id}/",
                        json={"status": "valide"},
                        timeout=5
                    )
                for stock_id in stock_ids:
                    requests.patch(
                        f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/{stock_id}/",
                        json={"statut": "valide"},
                        timeout=5
                    )

            return Response({"statut": decaissement.statut}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response(
                {"error": f"Impossible de mettre à jour les demandes : {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def demandes_disponibles(self, request):
        """
        Retourne toutes les demandes RH et Stock qui sont en attente pour créer un décaissement.
        """
        rh_demandes = []
        stock_demandes = []

        # 🔹 Récupérer les demandes RH en "en_attente"
        try:
            resp = requests.get(f"{settings.RH_SERVICE_URL}/api/demandes/", timeout=5)
            resp.raise_for_status()
            all_rh = resp.json()
            rh_demandes = [d for d in all_rh if d.get("status") == "en_attente"]
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes RH: {e}")

        # 🔹 Récupérer les demandes Stock en "en_attente"
        try:
            resp = requests.get(f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/", timeout=5)
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
