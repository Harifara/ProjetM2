# finance/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DemandeDecaissement, Depense
from .serializers import (
    DemandeDecaissementListSerializer,
    DemandeDecaissementDetailSerializer,
    DemandeDecaissementCreateSerializer,
    DepenseSerializer
)

# ==========================================================
# 1️⃣ FINANCE → CRUD DEMANDES DE DÉCAISSEMENT
# ==========================================================


# ➤ LISTE + CRÉATION
class DemandeDecaissementListCreateView(generics.ListCreateAPIView):
    queryset = DemandeDecaissement.objects.all().order_by('-created_at')
    serializer_class = DemandeDecaissementListSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DemandeDecaissementCreateSerializer
        return DemandeDecaissementListSerializer


# ➤ DÉTAIL + MODIFICATION
class DemandeDecaissementDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = DemandeDecaissement.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DemandeDecaissementCreateSerializer
        return DemandeDecaissementDetailSerializer


# ==========================================================
# 2️⃣ COORDINATEUR → VALIDATION / REJET
# ==========================================================

class DecaissementValidationView(APIView):

    def post(self, request, id):
        try:
            decaissement = DemandeDecaissement.objects.get(id=id)
        except DemandeDecaissement.DoesNotExist:
            return Response(
                {"error": "Décaissement introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        coordo_id = request.data.get("coordinateur_valideur_id")
        if coordo_id is None:
            return Response({"error": "coordinateur_valideur_id requis"}, status=400)

        try:
            decaissement.valider_par_coordonateur(coordo_id)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Décaissement validé avec succès"})


class DecaissementRejetView(APIView):

    def post(self, request, id):
        try:
            decaissement = DemandeDecaissement.objects.get(id=id)
        except DemandeDecaissement.DoesNotExist:
            return Response(
                {"error": "Décaissement introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        coordo_id = request.data.get("coordinateur_valideur_id")
        commentaire = request.data.get("commentaire", "")

        if coordo_id is None:
            return Response({"error": "coordinateur_valideur_id requis"}, status=400)

        try:
            decaissement.rejeter_par_coordonateur(coordo_id, commentaire)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Décaissement rejeté avec succès"})


# ==========================================================
# 3️⃣ LISTE DES DÉPENSES (générées automatiquement)
# ==========================================================

class DepenseListView(generics.ListAPIView):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer


class DepenseByDecaissementView(generics.ListAPIView):
    serializer_class = DepenseSerializer

    def get_queryset(self):
        return Depense.objects.filter(decaissement_id=self.kwargs["id"])

