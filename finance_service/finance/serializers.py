from rest_framework import serializers
from .models import DemandeDecaissement, Depense

# ----------------------------
# Serializer pour les dépenses (items)
# ----------------------------
class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ['id', 'description', 'montant', 'statut', 'date_creation']
        read_only_fields = ['id', 'date_creation']

# ----------------------------
# Serializer pour les demandes de décaissement
# ----------------------------
class DemandeDecaissementSerializer(serializers.ModelSerializer):
    depenses = DepenseSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    statut = serializers.CharField(read_only=True)  # Propriété calculée

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'source_service',
            'date_creation',
            'created_by',
            'total_montant',
            'statut',
            'envoyee',
            'total_items',
            'depenses'
        ]
        read_only_fields = ['id', 'date_creation', 'total_montant', 'statut']

    def get_total_items(self, obj):
        return sum(depense.montant for depense in obj.depenses.all())
