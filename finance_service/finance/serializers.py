from rest_framework import serializers
from .models import DemandeDecaissement, Depense

class DemandeDecaissementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields = ['id','reference','montant_total','statut','date_creation']

class DemandeDecaissementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields='__all__'
        read_only_fields=['id','reference','montant_total','statut','date_creation','date_decaissement']

class DemandeDecaissementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields=['demandes_rh_ids','demandes_stock_ids']
    def create(self, validated_data):
        user=self.context['request'].user
        return DemandeDecaissement.objects.create(cree_par_id=user.id, **validated_data)

class SoumettreCoordonnateurSerializer(serializers.Serializer):
    def save(self, **kwargs):
        decaissement = self.instance
        decaissement.soumettre_coordonnateur()
        return decaissement

class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields='__all__'
        read_only_fields=['id','date_depense']
    def validate(self, attrs):
        if attrs['decaissement'].statut != 'approuve':
            raise serializers.ValidationError("Décaissement non approuvé")
        return attrs
