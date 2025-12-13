# coordonnateur/serializers.py
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
        if ValidationCoordonnateur.objects.filter(
            demande_decaissement_id=attrs['demande_decaissement_id']
        ).exists():
            raise serializers.ValidationError(
                "Cette demande de décaissement a déjà été traitée."
            )
        if attrs.get('decision') not in ['approuve', 'rejete']:
            raise serializers.ValidationError("Décision invalide.")
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        validated_data['coordonnateur_id'] = request.user.id
        return super().create(validated_data)
