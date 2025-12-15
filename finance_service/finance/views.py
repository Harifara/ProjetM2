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
import jwt

# 🔹 Générer un JWT pour les requêtes inter-services
def get_service_jwt():
    payload = {
        "iss": "finance-service",
        "sub": "finance",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        en_reception = self.request.query_params.get("en_reception")
        if en_reception == "true":
            queryset = queryset.exclude(statut="decaisse")
        return queryset

    @action(detail=True, methods=["post"])
    def soumettre(self, request, pk=None):
        decaissement = self.get_object()
        token = get_service_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        try:
            # Mettre les demandes associées en "en_decaissement"
            for rh_id in decaissement.demandes_rh_ids:
                requests.post(
                    f"{settings.RH_SERVICE_URL}/api/rh/demandes/{rh_id}/en_decaissement/",
                    headers=headers,
                    timeout=5
                )
            for stock_id in decaissement.demandes_stock_ids:
                requests.post(
                    f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/{stock_id}/en_decaissement/",
                    headers=headers,
                    timeout=5
                )

            decaissement.soumettre_coordonnateur()
            return Response({"message": "Décaissement soumis au coordonnateur"}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({"error": f"Erreur service externe: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=True, methods=["post"])
    def appliquer_decision(self, request, pk=None):
        decaissement = self.get_object()
        decision = request.data.get("decision")
        token = get_service_jwt()
        headers = {"Authorization": f"Bearer {token}"}
        try:
            decaissement.appliquer_decision_coordonnateur(decision)

            # Si approuvé, mettre les demandes RH et Stock en "valide"
            if decision == "approuve":
                for rh_id in decaissement.demandes_rh_ids:
                    requests.post(
                        f"{settings.RH_SERVICE_URL}/api/rh/demandes/{rh_id}/approve/",
                        headers=headers,
                        timeout=5
                    )
                for stock_id in decaissement.demandes_stock_ids:
                    requests.post(
                        f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/{stock_id}/approve_finance/",
                        headers=headers,
                        timeout=5
                    )

            return Response({"statut": decaissement.statut}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({"error": f"Erreur service externe: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=False, methods=["get"])
    def demandes_disponibles(self, request):
        """
        Récupère toutes les demandes RH et Stock avec le statut 'en_attente'
        qui n'ont pas encore été utilisées dans un décaissement.
        """
        rh_demandes = []
        stock_demandes = []
        token = get_service_jwt()
        headers = {"Authorization": f"Bearer {token}"}

        # 🔹 Récupérer les demandes RH en attente
        try:
            resp = requests.get(f"{settings.RH_SERVICE_URL}/api/rh/demandes/", headers=headers)
            print(resp.text)
            resp.raise_for_status()
            rh_demandes = resp.json()
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes RH: {e}")

        # 🔹 Récupérer les demandes Stock en attente
        try:
            resp = requests.get(f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/", headers=headers)
            print(resp.text)
            resp.raise_for_status()
            stock_demandes = resp.json()
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes Stock: {e}")

        return Response({"rh": rh_demandes, "stock": stock_demandes})


class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        decaissement = serializer.validated_data["decaissement"]
        if decaissement.statut != "approuve":
            raise ValidationError("Décaissement non approuvé")
        serializer.save()
