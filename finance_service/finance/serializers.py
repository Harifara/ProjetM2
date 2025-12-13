from rest_framework import serializers
from decimal import Decimal

from .models import DemandeDecaissement, Depense


class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = [
            'id',
            'decaissement',
            'montant',
            'mode_paiement',
            'reference',
            'paye_par_id',
            'date_depense',
        ]
        read_only_fields = ['id', 'date_depense']

    def validate_montant(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "Le montant doit être supérieur à zéro."
            )
        return value

    def validate(self, attrs):
        decaissement = attrs.get('decaissement')
        if decaissement.statut != 'approuve':
            raise serializers.ValidationError(
                "Une dépense ne peut être créée que pour un décaissement approuvé."
            )
        return attrs


class DemandeDecaissementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'montant_total',
            'statut',
            'date_creation',
            'date_decaissement',
        ]


class DemandeDecaissementDetailSerializer(serializers.ModelSerializer):
    depenses = DepenseSerializer(many=True, read_only=True)

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'demandes_rh_ids',
            'demandes_stock_ids',
            'montant_total',
            'statut',
            'cree_par_id',
            'date_creation',
            'date_decaissement',
            'depenses',
        ]


class DemandeDecaissementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'demandes_rh_ids',
            'demandes_stock_ids',
            'montant_total',
            'cree_par_id',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if not attrs.get('demandes_rh_ids') and not attrs.get('demandes_stock_ids'):
            raise serializers.ValidationError(
                "Au moins une demande RH ou Stock est obligatoire."
            )

        if attrs.get('montant_total', Decimal('0')) <= Decimal('0'):
            raise serializers.ValidationError(
                "Le montant total doit être supérieur à zéro."
            )

        return attrs


class SoumettreCoordonnateurSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.soumettre_coordonnateur()
        return instance


