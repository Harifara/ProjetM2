from rest_framework import serializers
from .models import DemandeDecaissement, DemandeDecaissementItem, Depense

# ----------------------------
# Serializer pour les dépenses
# ----------------------------
class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ['id', 'item_decaissement', 'montant', 'date_creation', 'statut_paiement']
        read_only_fields = ['id', 'date_creation']


# ----------------------------
# Serializer pour les items de décaissement
# ----------------------------
class DemandeDecaissementItemSerializer(serializers.ModelSerializer):
    depense = DepenseSerializer(read_only=True)  # inclure la dépense si elle existe

    class Meta:
        model = DemandeDecaissementItem
        fields = ['id', 'decaissement', 'description', 'montant', 'statut', 'depense']
        read_only_fields = ['id', 'depense']


# ----------------------------
# Serializer pour les décaissements
# ----------------------------
class DemandeDecaissementSerializer(serializers.ModelSerializer):
    items = DemandeDecaissementItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'source_demande_rh_id',
            'source_demande_stock_id',
            'date_creation',
            'statut',
            'total_montant',
            'total_items',
            'created_by',
            'items'
        ]
        read_only_fields = ['id', 'date_creation', 'statut', 'total_montant']

    def get_total_items(self, obj):
        # Calcule le total des montants des items liés
        return sum(item.montant for item in obj.items.all())
