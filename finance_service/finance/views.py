from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings

from .models import DemandeDecaissement, Depense
from .serializers import (
    DepenseSerializer,
    DemandeDecaissementListSerializer,
    DemandeDecaissementDetailSerializer,
    DemandeDecaissementCreateSerializer,
    SoumettreCoordonnateurSerializer,
)



class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return DemandeDecaissementListSerializer
        if self.action == 'retrieve':
            return DemandeDecaissementDetailSerializer
        if self.action == 'create':
            return DemandeDecaissementCreateSerializer
        if self.action == 'soumettre_coordonnateur':
            return SoumettreCoordonnateurSerializer
        return DemandeDecaissementDetailSerializer

    @action(detail=True, methods=['post'], url_path='soumettre')
    def soumettre_coordonnateur(self, request, pk=None):
        decaissement = self.get_object()

        serializer = SoumettreCoordonnateurSerializer(
            decaissement, data={}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Demande soumise au coordonnateur."},
            status=status.HTTP_200_OK
        )

        
class DemandesDisponiblesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rh_used, stock_used = DemandeDecaissement.get_demandes_deja_utilisees()

        try:
            resp_rh = requests.get(
                f"{settings.RH_SERVICE_URL}/api/demandes/?status__in=en_attente,en_cours,approuve",
                timeout=5
            )
            resp_rh.raise_for_status()
            rh_all = resp_rh.json()
        except requests.RequestException:
            rh_all = []

        rh_available = [d for d in rh_all if d['id'] not in rh_used]

        try:
            resp_stock = requests.get(
                f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/?statut__in=en_attente,approuve",
                timeout=5
            )
            resp_stock.raise_for_status()
            stock_all = resp_stock.json()
        except requests.RequestException:
            stock_all = []

        stock_available = [d for d in stock_all if d['id'] not in stock_used]

        return Response({
            "rh": rh_available,
            "stock": stock_available
        })



class DecisionDecaissementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, decaissement_id):
        decision = request.data.get('decision')

        try:
            decaissement = DemandeDecaissement.objects.get(id=decaissement_id)
        except DemandeDecaissement.DoesNotExist:
            return Response(
                {"detail": "Décaissement introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        if decaissement.statut != 'en_attente_coordonnateur':
            return Response(
                {"detail": "Décaissement déjà traité"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if decision == 'approuve':
            decaissement.approuver()
        elif decision == 'rejete':
            decaissement.rejeter()
        else:
            return Response(
                {"detail": "Décision invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"statut": decaissement.statut},
            status=status.HTTP_200_OK
        )

class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]


