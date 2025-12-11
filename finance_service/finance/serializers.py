# finance/serializers.py
from rest_framework import serializers
from .models import DemandeDecaissement, Depense, DepenseFinale

class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = [
            'id',
            'description',
            'montant',
            'statut',
            'date_creation',
        ]

class DepenseFinaleSerializer(serializers.ModelSerializer):
    depense = DepenseSerializer(read_only=True)

    class Meta:
        model = DepenseFinale
        fields = [
            'id',
            'depense',
            'montant',
            'date_creation',
            'paye',
        ]

class DemandeDecaissementSerializer(serializers.ModelSerializer):
    depenses = DepenseSerializer(many=True, read_only=True)
    statut = serializers.CharField(read_only=True)  # <-- retirer source='statut'

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'source_service',
            'created_by',
            'date_creation',
            'demande_id',
            'demandeAchat_id',
            'envoyee',
            'coordo_decision',
            'coordo_id',
            'coordo_date',
            'coordo_commentaire',
            'total_montant',
            'statut',
            'depenses',
        ]
