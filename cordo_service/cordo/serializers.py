from rest_framework import serializers
from .models import ValidationCoordonnateur

class ValidationCoordonnateurSerializer(serializers.ModelSerializer):
    class Meta:
        model=ValidationCoordonnateur
        fields='__all__'
        read_only_fields=['id','coordonnateur_id','date_validation']

class ValidationCoordonnateurCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=ValidationCoordonnateur
        fields=['demande_decaissement_id','decision','commentaire']
    def validate_decision(self,value):
        if value not in ['approuve','rejete']:
            raise serializers.ValidationError("Décision invalide")
        return value
    def create(self, validated_data):
        validated_data['coordonnateur_id']=self.context['request'].user.id
        obj,_ = ValidationCoordonnateur.objects.update_or_create(
            demande_decaissement_id=validated_data['demande_decaissement_id'],
            defaults=validated_data
        )
        return obj
