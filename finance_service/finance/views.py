from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DemandeDecaissement, DemandeDecaissementItem
from .serializers import (
    DemandeDecaissementSerializer,
    DemandeDecaissementItemSerializer
)

# ----------------------------
# Liste et création des décaissements
# ----------------------------
class DemandeDecaissementListCreateView(generics.ListCreateAPIView):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer

    def create(self, request, *args, **kwargs):
        """
        Création d'un décaissement avec ses items en nested.
        La création d'items se fait via un champ `items` dans la requête.
        """
        items_data = request.data.pop('items', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decaissement = serializer.save()

        # Crée les items
        for item in items_data:
            DemandeDecaissementItem.objects.create(
                decaissement=decaissement,
                **item
            )

        decaissement.calculer_total()
        decaissement.mettre_a_jour_statut()

        return Response(
            self.get_serializer(decaissement).data,
            status=status.HTTP_201_CREATED
        )

# ----------------------------
# Détail d’un décaissement
# ----------------------------
class DemandeDecaissementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DemandeDecaissement.objects.all()
    serializer_class = DemandeDecaissementSerializer
    lookup_field = 'id'

# ----------------------------
# Liste et création des items (optionnel)
# ----------------------------
class DemandeDecaissementItemListCreateView(generics.ListCreateAPIView):
    queryset = DemandeDecaissementItem.objects.all()
    serializer_class = DemandeDecaissementItemSerializer

    def create(self, request, *args, **kwargs):
        """
        Création d'un item pour un décaissement existant
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        # Mettre à jour le décaissement parent
        item.decaissement.calculer_total()
        item.decaissement.mettre_a_jour_statut()

        return Response(
            self.get_serializer(item).data,
            status=status.HTTP_201_CREATED
        )

# ----------------------------
# Mise à jour du statut d’un item (validation par coordinateur)
# ----------------------------
class DemandeDecaissementItemUpdateStatusView(APIView):
    def post(self, request, item_id):
        """
        Met à jour le statut d'un item de décaissement
        Exemple de payload: {"statut": "valide"}
        """
        try:
            item = DemandeDecaissementItem.objects.get(id=item_id)
        except DemandeDecaissementItem.DoesNotExist:
            return Response({"detail": "Item non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        statut = request.data.get('statut')
        if statut not in ['en_attente', 'valide', 'rejete']:
            return Response({"detail": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)

        item.statut = statut
        item.save()

        # Le signal post_save s'occupera de créer la dépense si nécessaire
        return Response(DemandeDecaissementItemSerializer(item).data)
