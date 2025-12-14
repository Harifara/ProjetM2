# finance/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementSerializer, DepenseSerializer


class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les demandes de décaissement.
    """
    queryset = DemandeDecaissement.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = DemandeDecaissementSerializer

    def get_queryset(self):
        """
        On filtre pour retourner uniquement les demandes non encore décaisées
        si on est dans la liste des demandes reçues.
        """
        queryset = super().get_queryset()
        # Filtrer les demandes à afficher sur la page "demandes reçues"
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
            return Response(
                {"statut": decaissement.statut}, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
