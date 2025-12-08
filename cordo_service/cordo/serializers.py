from rest_framework import serializers
from .models import ValidationCoordinateur

class ValidationCoordinateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordinateur
        fields = ['id', 'item_decaissement', 'coordinateur_id', 'statut', 'commentaire', 'date_validation']
