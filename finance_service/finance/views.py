# finance/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementSerializer, DepenseSerializer


# Liste + création des demandes
class DemandeDecaissementListCreateView(generics.ListCreateAPIView):
    queryset = DemandeDecaissement.objects.all().order_by('-date_creation')
    serializer_class = DemandeDecaissementSerializer


# Détail / update d'une demande
class DemandeDecaissementDetailUpdateView(generics.RetrieveUpdateAPIView):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer
    lookup_field = 'id'


# Endpoint pour "envoyer" la demande au coordonnateur
# (marque envoyee = True)
class DemandeEnvoyerCoordoView(APIView):
    def post(self, request, id):
        demande = get_object_or_404(DemandeDecaissement, id=id)
        if demande.envoyee:
            return Response({"detail": "Déjà envoyée au coordonnateur."}, status=status.HTTP_400_BAD_REQUEST)

        demande.envoyee = True
        demande.save(update_fields=['envoyee'])
        return Response({"detail": "Demande envoyée au coordonnateur."}, status=status.HTTP_200_OK)


# Validation par le coordonnateur :
# - marque coordo_decision = 'valide'
# - stocke coordo_id, coordo_date, coordo_commentaire
# - crée les Depense à partir d'une liste fournie dans body (optionnel)
#   body attendu: { "depenses": [{"description": "...", "montant": "123.45"}, ...] }
class DemandeValiderCoordoView(APIView):
    def post(self, request, id):
        demande = get_object_or_404(DemandeDecaissement, id=id)

        if not demande.envoyee:
            return Response({"detail": "La demande doit être envoyée au coordonnateur avant validation."},
                            status=status.HTTP_400_BAD_REQUEST)

        if demande.coordo_decision == 'valide':
            return Response({"detail": "La demande est déjà validée."}, status=status.HTTP_400_BAD_REQUEST)

        # Enregistrer décision
        demande.coordo_decision = 'valide'
        demande.coordo_id = request.data.get('coordo_id')  # optionnel
        demande.coordo_commentaire = request.data.get('coordo_commentaire', '')
        demande.coordo_date = timezone.now()
        demande.save(update_fields=['coordo_decision', 'coordo_id', 'coordo_commentaire', 'coordo_date'])

        # Si on fournit des dépenses à créer, on les crée ici.
        depenses_payload = request.data.get('depenses', None)
        created_depenses = []
        if isinstance(depenses_payload, list):
            for item in depenses_payload:
                desc = item.get('description', '')
                montant = item.get('montant')
                if montant is None:
                    continue
                ser = DepenseSerializer(data={
                    "demande": str(demande.id),
                    "description": desc,
                    "montant": montant,
                    "statut": "valide"  # On crée comme validée puisque coordo a validé la demande
                })
                ser.is_valid(raise_exception=True)
                dep = ser.save()
                created_depenses.append(DepenseSerializer(dep).data)

        # Recalculer total
        demande.calculer_total()

        data = DemandeDecaissementSerializer(demande).data
        data['created_depenses'] = created_depenses
        return Response(data, status=status.HTTP_200_OK)


# Rejet par le coordonnateur
class DemandeRejeterCoordoView(APIView):
    def post(self, request, id):
        demande = get_object_or_404(DemandeDecaissement, id=id)

        if not demande.envoyee:
            return Response({"detail": "La demande doit être envoyée au coordonnateur avant rejet."},
                            status=status.HTTP_400_BAD_REQUEST)

        if demande.coordo_decision == 'rejete':
            return Response({"detail": "La demande est déjà rejetée."}, status=status.HTTP_400_BAD_REQUEST)

        demande.coordo_decision = 'rejete'
        demande.coordo_id = request.data.get('coordo_id')
        demande.coordo_commentaire = request.data.get('coordo_commentaire', '')
        demande.coordo_date = timezone.now()
        demande.save(update_fields=['coordo_decision', 'coordo_id', 'coordo_commentaire', 'coordo_date'])

        return Response(DemandeDecaissementSerializer(demande).data, status=status.HTTP_200_OK)


# Créer une dépense (seulement autorisée si la demande a été validée par coordo)
class DepenseCreateView(APIView):
    def post(self, request):
        # body attendu: { "demande": "<uuid>", "description": "...", "montant": "123.45" }
        ser = DepenseSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        # Vérifier que la demande existe et est validée par coordo
        demande_id = ser.validated_data['demande'].id if hasattr(ser.validated_data['demande'], 'id') else ser.validated_data['demande']
        # More straightforward: fetch demande separately
        from .models import DemandeDecaissement
        demande = get_object_or_404(DemandeDecaissement, id=ser.validated_data['demande'].id if hasattr(ser.validated_data['demande'], 'id') else ser.validated_data['demande'])
        if demande.coordo_decision != 'valide':
            return Response({"detail": "Impossible d'ajouter une dépense : la demande n'est pas validée par le coordonnateur."},
                            status=status.HTTP_400_BAD_REQUEST)

        dep = ser.save()
        # Recalcul total
        dep.demande.calculer_total()
        return Response(DepenseSerializer(dep).data, status=status.HTTP_201_CREATED)


# Valider / rejeter une DEPENSE (coordo ou finance selon process) - simple endpoints
class DepenseValidationView(APIView):
    def post(self, request, depense_id):
        dep = get_object_or_404(Depense, id=depense_id)
        dep.statut = 'valide'
        dep.save()
        return Response(DepenseSerializer(dep).data, status=status.HTTP_200_OK)


class DepenseRejetView(APIView):
    def post(self, request, depense_id):
        dep = get_object_or_404(Depense, id=depense_id)
        dep.statut = 'rejete'
        dep.save()
        return Response(DepenseSerializer(dep).data, status=status.HTTP_200_OK)
