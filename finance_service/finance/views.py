from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementCreateSerializer, DepenseSerializer, SoumettreCoordonnateurSerializer

class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementCreateSerializer
    permission_classes=[IsAuthenticated]

    @action(detail=True, methods=['post'])
    def soumettre(self, request, pk=None):
        decaissement=self.get_object()
        decaissement.soumettre_coordonnateur()
        return Response({"message":"Soumis au coordonnateur"})

class DecisionDecaissementView(APIView):
    def post(self, request, decaissement_id):
        decaissement=get_object_or_404(DemandeDecaissement,id=decaissement_id)
        decaissement.appliquer_decision_coordonnateur(request.data.get("decision"))
        return Response({"statut": decaissement.statut})

class DepenseViewSet(viewsets.ModelViewSet):
    queryset=Depense.objects.all()
    serializer_class=DepenseSerializer
    permission_classes=[IsAuthenticated]
    def perform_create(self, serializer):
        if serializer.validated_data['decaissement'].statut!='approuve':
            raise ValidationError("Décaissement non approuvé")
        serializer.save()
