from rest_framework import serializers
from .models import DemandeDecaissement, DemandeDecaissementItem, Depense
from coordinator.models import ValidationCoordinateur

# ------------------------
# Serializer Item Décaissement
# ------------------------
class DemandeDecaissementItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissementItem
        fields = ['id', 'decaissement', 'description', 'montant', 'statut']

# ------------------------
# Serializer Décaissement
# ------------------------
class DemandeDecaissementSerializer(serializers.ModelSerializer):
    items = DemandeDecaissementItemSerializer(many=True, read_only=True)

    class Meta:
        model = DemandeDecaissement
        fields = ['id', 'source_demande_rh', 'source_demande_stock', 'date_creation', 
                  'statut', 'total_montant', 'created_by', 'items']

# ------------------------
# Serializer Dépense
# ------------------------
class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ['id', 'item_decaissement', 'montant', 'date_creation', 'statut_paiement']
