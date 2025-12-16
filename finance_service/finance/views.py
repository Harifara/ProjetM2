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
    permission_classes = [IsAuthenticated]
    serializer_class = DemandeDecaissementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        en_reception = self.request.query_params.get("en_reception")
        if en_reception == "true":
            queryset = queryset.exclude(statut="decaisse")
        return queryset

    @action(detail=True, methods=["post"])
    def soumettre(self, request, pk=None):
        decaissement = self.get_object()
        try:
            decaissement.soumettre_coordonnateur()
            return Response({"message": "Décaissement soumis au coordonnateur"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def appliquer_decision(self, request, pk=None):
        decaissement = self.get_object()
        decision = request.data.get("decision")
        if decision not in ["approuve", "rejete"]:
            return Response({"error": "Décision invalide"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            decaissement.appliquer_decision_coordonnateur(decision)
            return Response({"statut": decaissement.statut}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def demandes_disponibles(self, request):
        """
        Récupère toutes les demandes RH et Stock avec le statut 'en_attente'
        qui ne sont pas déjà utilisées dans un décaissement.
        """
        rh_demandes, stock_demandes = [], []
        token = get_service_jwt()
        headers = {"Authorization": f"Bearer {token}"}

        # 🔹 Demandes RH
        try:
            resp = requests.get(
                f"{settings.RH_SERVICE_URL}/api/rh/demandes/",
                headers=headers,
                params={"status": "en_attente"},
                timeout=5
            )
            resp.raise_for_status()
            rh_demandes = resp.json()
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes RH: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[Finance] Contenu réponse RH: {e.response.text}")

        # 🔹 Demandes Stock
        try:
            resp = requests.get(
                f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/",
                headers=headers,
                params={"statut": "en_attente"},
                timeout=5
            )
            resp.raise_for_status()
            stock_demandes = resp.json()
        except requests.RequestException as e:
            print(f"[Finance] Impossible de récupérer les demandes Stock: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[Finance] Contenu réponse Stock: {e.response.text}")

        # 🔹 Filtrer les demandes déjà utilisées
        rh_ids_utilises, stock_ids_utilises = DemandeDecaissement.get_demandes_deja_utilisees()
        rh_demandes = [d for d in rh_demandes if d["id"] not in rh_ids_utilises]
        stock_demandes = [d for d in stock_demandes if d["id"] not in stock_ids_utilises]

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
