from rest_framework import serializers
from .models import DemandeDecaissement, Depense

class DemandeDecaissementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields = ['id', 'reference', 'montant_total', 'statut', 'date_creation']

class DemandeDecaissementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields = '__all__'
        read_only_fields = [
            'id', 'reference', 'montant_total', 'statut',
            'date_creation', 'date_decaissement', 'cree_par_id'
        ]

class DemandeDecaissementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields = ['demandes_rh_ids', 'demandes_stock_ids']

    def create(self, validated_data):
        user = self.context['request'].user
        instance = DemandeDecaissement.objects.create(
            cree_par_id=user.id, **validated_data
        )
        # recalcul automatique du montant total
        instance.recalculer_montant_total()
        instance.save()
        return instance

class SoumettreCoordonnateurSerializer(serializers.Serializer):
    def save(self, **kwargs):
        decaissement = self.instance
        decaissement.soumettre_coordonnateur()
        return decaissement

class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = '__all__'
        read_only_fields = ['id', 'date_depense']

    def validate(self, attrs):
        decaissement = attrs['decaissement']
        if decaissement.statut != 'approuve':
            raise serializers.ValidationError("Décaissement non approuvé")
        return attrs
