# finance/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import DemandeDecaissement, Depense
from .serializers import DemandeDecaissementSerializer, DepenseSerializer

# ----------------------------
# DemandeDecaissement ViewSet
# ----------------------------
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all().order_by('-date_creation')
    serializer_class = DemandeDecaissementSerializer
    lookup_field = 'id'

    @action(detail=True, methods=['post'], url_path='envoyer')
    def envoyer(self, request, id=None):
        demande = self.get_object()
        if demande.envoyee:
            return Response({"detail": "Déjà envoyée au coordonnateur."}, status=status.HTTP_400_BAD_REQUEST)
        demande.envoyee = True
        demande.save(update_fields=['envoyee'])
        return Response({"detail": "Demande envoyée au coordonnateur."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='valider-coordo')
    def valider_coordo(self, request, id=None):
        demande = self.get_object()
        if not demande.envoyee:
            return Response({"detail": "La demande doit être envoyée au coordonnateur avant validation."},
                            status=status.HTTP_400_BAD_REQUEST)
        if demande.coordo_decision == 'valide':
            return Response({"detail": "La demande est déjà validée."}, status=status.HTTP_400_BAD_REQUEST)

        demande.coordo_decision = 'valide'
        demande.coordo_id = request.data.get('coordo_id')
        demande.coordo_commentaire = request.data.get('coordo_commentaire', '')
        demande.coordo_date = timezone.now()
        demande.save(update_fields=['coordo_decision', 'coordo_id', 'coordo_commentaire', 'coordo_date'])

        # Création des dépenses si fournies
        depenses_payload = request.data.get('depenses', [])
        created_depenses = []
        for item in depenses_payload:
            montant = item.get('montant')
            if montant is None:
                continue
            ser = DepenseSerializer(data={
                "demande": str(demande.id),
                "description": item.get('description', ''),
                "montant": montant,
                "statut": "valide"
            })
            ser.is_valid(raise_exception=True)
            dep = ser.save()
            created_depenses.append(DepenseSerializer(dep).data)

        demande.calculer_total()
        data = DemandeDecaissementSerializer(demande).data
        data['created_depenses'] = created_depenses
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rejeter-coordo')
    def rejeter_coordo(self, request, id=None):
        demande = self.get_object()
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


# ----------------------------
# Depense ViewSet
# ----------------------------
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    lookup_field = 'depense_id'

    def create(self, request, *args, **kwargs):
        ser = DepenseSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        demande_id = ser.validated_data['demande'].id if hasattr(ser.validated_data['demande'], 'id') else ser.validated_data['demande']
        demande = get_object_or_404(DemandeDecaissement, id=demande_id)
        if demande.coordo_decision != 'valide':
            return Response({"detail": "Impossible d'ajouter une dépense : la demande n'est pas validée par le coordonnateur."},
                            status=status.HTTP_400_BAD_REQUEST)
        dep = ser.save()
        dep.demande.calculer_total()
        return Response(DepenseSerializer(dep).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='valider')
    def valider(self, request, depense_id=None):
        dep = self.get_object()
        dep.statut = 'valide'
        dep.save()
        return Response(DepenseSerializer(dep).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='rejeter')
    def rejeter(self, request, depense_id=None):
        dep = self.get_object()
        dep.statut = 'rejete'
        dep.save()
        return Response(DepenseSerializer(dep).data, status=status.HTTP_200_OK)
