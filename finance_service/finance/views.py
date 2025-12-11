from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

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
        decaissement = get_object_or_404(DemandeDecaissement, id=id)

        coordo_id = request.data.get("coordinateur_valideur_id")
        if not coordo_id:
            return Response({"error": "coordinateur_valideur_id requis"}, status=400)

        try:
            decaissement.valider_par_coordonateur(coordo_id)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Décaissement validé avec succès"}, status=200)


class DecaissementRejetView(APIView):

    def post(self, request, id):
        decaissement = get_object_or_404(DemandeDecaissement, id=id)

        coordo_id = request.data.get("coordinateur_valideur_id")
        commentaire = request.data.get("commentaire", "")

        if not coordo_id:
            return Response({"error": "coordinateur_valideur_id requis"}, status=400)

        try:
            decaissement.rejeter_par_coordonateur(coordo_id, commentaire)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Décaissement rejeté avec succès"}, status=200)


# ==========================================================
# 3️⃣ LISTE DES DÉPENSES (générées automatiquement)
# ==========================================================

class DepenseListView(generics.ListAPIView):
    queryset = Depense.objects.all().order_by('-date_paiement')
    serializer_class = DepenseSerializer


class DepenseByDecaissementView(generics.ListAPIView):
    serializer_class = DepenseSerializer

    def get_queryset(self):
        decaissement_id = self.kwargs.get("id")
        return Depense.objects.filter(decaissement_id=decaissement_id).order_by('-date_paiement')
