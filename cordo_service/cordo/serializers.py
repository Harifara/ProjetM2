from rest_framework import serializers
from .models import ValidationCoordinateur

class ValidationCoordinateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordinateur
        # Tous les champs nécessaires
        fields = [
            'id',
            'item_decaissement_id',  # UUID de l'item dans finance_service
            'coordinateur_id',       # UUID de l'utilisateur coordinateur
            'statut',                # 'valide' ou 'rejete'
            'commentaire',           # optionnel
            'date_validation',       # date automatique
        ]
        # Champs générés automatiquement ou non modifiables côté client
        read_only_fields = ['id', 'date_validation']
