from rest_framework import serializers
from .models import DemandeDecaissement, Depense, DepenseFinale

# ----------------------------
# Serializer pour les Dépenses
# ----------------------------
class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = ['id', 'description', 'montant', 'statut', 'date_creation']
        read_only_fields = ['id', 'date_creation']


# ----------------------------
# Serializer pour les Dépenses Finales
# ----------------------------
class DepenseFinaleSerializer(serializers.ModelSerializer):
    depense = DepenseSerializer(read_only=True)

    class Meta:
        model = DepenseFinale
        fields = ['id', 'depense', 'montant', 'date_creation', 'paye']
        read_only_fields = ['id', 'depense', 'date_creation']


# ----------------------------
# Serializer pour les Demandes de Décaissement
# ----------------------------
class DemandeDecaissementSerializer(serializers.ModelSerializer):
    depenses = DepenseSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    statut = serializers.CharField(read_only=True)

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'source_service',
            'created_by',
            'date_creation',
            'envoyee',
            'total_montant',
            'statut',
            'total_items',
            'depenses'
        ]
        read_only_fields = ['id', 'date_creation', 'total_montant', 'statut', 'total_items']

    def get_total_items(self, obj):
        """Retourne le montant total de toutes les dépenses liées."""
        return sum(dep.montant for dep in obj.depenses.all())
