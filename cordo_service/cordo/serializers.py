from rest_framework import serializers
from .models import ValidationCoordinateur

class ValidationCoordinateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordinateur
        fields = [
            'id',
            'item_decaissement_id',  # correction ici
            'coordinateur_id',
            'statut',
            'commentaire',
            'date_validation'
        ]
        read_only_fields = ['id', 'date_validation']
