from rest_framework import serializers
from .models import DemandeDecaissement, DemandeDecaissementItem, Depense

# ----------------------------
# Serializer pour les items
# ----------------------------
class DemandeDecaissementItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissementItem
        fields = ['id', 'decaissement', 'description', 'montant', 'statut']


# ----------------------------
# Serializer pour les décaissements
# ----------------------------
class DemandeDecaissementSerializer(serializers.ModelSerializer):
    items = DemandeDecaissementItemSerializer(many=True, read_only=True)

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'source_demande_rh_id',
            'source_demande_stock_id',
            'date_creation',
            'statut',
            'total_montant',
            'created_by',
            'items'
        ]


# ----------------------------
# Serializer pour les dépenses
# ----------------------------
class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ['id', 'item_decaissement', 'montant', 'date_creation', 'statut_paiement']


