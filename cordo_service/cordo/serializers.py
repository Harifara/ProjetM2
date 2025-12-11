# coordonateur/serializers.py

from rest_framework import serializers
from .models import ValidationCoordinateur
from finance.models import DemandeDecaissement

# ----------------------------
# Serializer pour la validation
# ----------------------------
class ValidationCoordinateurSerializer(serializers.ModelSerializer):
    # Optionnel : afficher certaines infos de la demande directement
    decaissement_numero = serializers.SerializerMethodField()
    total_montant = serializers.SerializerMethodField()
    coordo_decision = serializers.CharField(source='decaissement.coordo_decision', read_only=True)

    class Meta:
        model = ValidationCoordinateur
        fields = [
            'id',
            'decaissement',
            'decaissement_numero',
            'total_montant',
            'decision',
            'commentaire',
            'coordinateur_id',
            'date_decision',
            'coordo_decision'
        ]
        read_only_fields = ['id', 'date_decision', 'decaissement_numero', 'total_montant', 'coordo_decision']

    def get_decaissement_numero(self, obj):
        # On peut renvoyer l'id ou un champ spécifique comme numéro si ajouté
        return str(obj.decaissement.id)

    def get_total_montant(self, obj):
        return obj.decaissement.total_montant


# ----------------------------
# Serializer pour la liste des demandes à valider
# ----------------------------
class DemandeDecaissementCoordoSerializer(serializers.ModelSerializer):
    validations = ValidationCoordinateurSerializer(many=True, read_only=True)
    statut = serializers.CharField(source='statut', read_only=True)

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'source_service',
            'date_creation',
            'total_montant',
            'statut',
            'validations'
        ]
        read_only_fields = ['id', 'date_creation', 'total_montant', 'statut', 'validations']
