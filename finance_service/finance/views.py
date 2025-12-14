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
    SoumettreCoordonnateurSerializer
)

class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return DemandeDecaissementListSerializer
        elif self.action in ['retrieve']:
            return DemandeDecaissementDetailSerializer
        return DemandeDecaissementCreateSerializer

    @action(detail=True, methods=['post'])
    def soumettre(self, request, pk=None):
        decaissement = self.get_object()
        try:
            decaissement.soumettre_coordonnateur()
            return Response({"message": "Soumis au coordonnateur"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        decaissement = serializer.validated_data['decaissement']
        if decaissement.statut != 'approuve':
            raise ValidationError("Décaissement non approuvé")
        serializer.save()
