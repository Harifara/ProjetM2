from rest_framework import serializers
from .models import ValidationCoordonnateur

class ValidationCoordonnateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordonnateur
        fields = [
            'id',
            'decaissement_id',
            'coordo_id',
            'decision',
            'commentaire',
            'date_decision',
        ]
