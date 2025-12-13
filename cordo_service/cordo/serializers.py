from rest_framework import serializers
from django.utils import timezone

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
        read_only_fields = ['id', 'date_validation']


class ValidationCoordonnateurCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationCoordonnateur
        fields = [
            'id',
            'demande_decaissement_id',
            'coordonnateur_id',
            'decision',
            'commentaire',
        ]
        read_only_fields = ['id']

    def validate_decision(self, value):
        if value not in ['approuve', 'rejete']:
            raise serializers.ValidationError("Décision invalide.")
        return value

    def validate(self, attrs):
        # Un seul avis par décaissement
        if ValidationCoordonnateur.objects.filter(
            demande_decaissement_id=attrs['demande_decaissement_id']
        ).exists():
            raise serializers.ValidationError(
                "Cette demande de décaissement a déjà été validée."
            )
        return attrs

    def create(self, validated_data):
        validation = ValidationCoordonnateur.objects.create(**validated_data)

        # Appel inter-service vers Finance (à faire dans la vue ou via signal)
        # ex: finance_api.update_statut_decaissement(
        #         validation.demande_decaissement_id,
        #         validation.decision
        #     )

        return validation

class DecisionCoordonnateurSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=['approuve', 'rejete'])
    commentaire = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        demande_id = validated_data['demande_decaissement_id']

        validation = ValidationCoordonnateur(
            demande_decaissement_id=demande_id,
            coordonnateur_id=validated_data['coordonnateur_id'],
        )

        if validated_data['decision'] == 'approuve':
            validation.valider()
        else:
            validation.rejeter(validated_data.get('commentaire', ''))

        return validation
