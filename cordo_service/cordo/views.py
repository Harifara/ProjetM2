# coordonateur/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from finance.models import DemandeDecaissement
from .models import ValidationCoordinateur
from .serializers import ValidationCoordinateurSerializer, DemandeDecaissementCoordoSerializer

# ----------------------------
# Liste des demandes à valider
# ----------------------------
class DemandesCoordoListView(generics.ListAPIView):
    serializer_class = DemandeDecaissementCoordoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtrer uniquement les demandes envoyées au coordonnateur et non encore traitées
        return DemandeDecaissement.objects.filter(envoyee=True, coordo_decision='non_traite').order_by('-date_creation')


# ----------------------------
# Créer une validation (valide / rejete)
# ----------------------------
class ValidationCoordoCreateView(generics.CreateAPIView):
    serializer_class = ValidationCoordinateurSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        decaissement_id = request.data.get('decaissement')
        decision = request.data.get('decision')
        commentaire = request.data.get('commentaire', '')

        # Vérification du décaissement
        decaissement = get_object_or_404(DemandeDecaissement, id=decaissement_id)

        # Création de la validation
        validation = ValidationCoordinateur.objects.create(
            decaissement=decaissement,
            decision=decision,
            commentaire=commentaire,
            coordinateur_id=request.user.id  # supposé que l'utilisateur est authentifié
        )

        # Mise à jour du décaissement côté finance
        if decision == 'valide':
            decaissement.coordo_decision = 'valide'
        elif decision == 'rejete':
            decaissement.coordo_decision = 'rejete'
        decaissement.coordo_id = request.user.id
        decaissement.coordo_date = validation.date_decision
        decaissement.coordo_commentaire = commentaire
        decaissement.save(update_fields=['coordo_decision', 'coordo_id', 'coordo_date', 'coordo_commentaire'])

        serializer = self.get_serializer(validation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ----------------------------
# Détail d'une validation
# ----------------------------
class ValidationCoordoDetailView(generics.RetrieveAPIView):
    queryset = ValidationCoordinateur.objects.all()
    serializer_class = ValidationCoordinateurSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
