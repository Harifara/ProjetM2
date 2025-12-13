from rest_framework import serializers
from .models import ValidationCoordonnateur


class ValidationCoordonnateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordonnateur
        fields = [
            'id',
            'demande_decaissement_id',
            'coordonnateur_id',
            'decision',
            'commentaire',
            'date_validation',
        ]
        read_only_fields = ['id', 'coordonnateur_id', 'date_validation']


class ValidationCoordonnateurCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordonnateur
        fields = [
            'demande_decaissement_id',
            'decision',
            'commentaire',
        ]

    def validate(self, attrs):
        # Vérifie uniquement la décision
        if attrs.get('decision') not in ['approuve', 'rejete']:
            raise serializers.ValidationError("Décision invalide.")
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['coordonnateur_id'] = request.user.id

        # Utilisation de update_or_create pour éviter les erreurs 400 si déjà existant
        obj, created = ValidationCoordonnateur.objects.update_or_create(
            demande_decaissement_id=validated_data['demande_decaissement_id'],
            defaults={
                'coordonnateur_id': validated_data['coordonnateur_id'],
                'decision': validated_data['decision'],
                'commentaire': validated_data.get('commentaire', ''),
            }
        )
        return obj
