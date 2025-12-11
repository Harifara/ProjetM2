from rest_framework import serializers
from .models import ValidationCoordinateur
from finance.serializers import DemandeDecaissementListSerializer

class ValidationCoordinateurSerializer(serializers.ModelSerializer):
    # Nested serializer pour afficher le décaissement associé
    decaissement_detail = DemandeDecaissementListSerializer(
        source='decaissement', read_only=True
    )

    class Meta:
        model = ValidationCoordinateur
        fields = [
            'id',
            'decaissement',
            'decaissement_detail',
            'decision',
            'commentaire',
            'coordinateur_id',
            'date_decision',
        ]
        read_only_fields = ['id', 'date_decision', 'decaissement_detail']

# Serializer pour la création simple (POST)
class ValidationCoordinateurCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordinateur
        fields = [
            'decaissement',
            'decision',
            'commentaire',
            'coordinateur_id',
        ]
