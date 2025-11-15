from rest_framework import serializers
from .models import (
    TypeDecaissement,
    DemandeDecaissement,
    Depense,
    BulletinPaie,
    ValidationDemande
)


# =========================
# Serializer TypeDecaissement
# =========================
class TypeDecaissementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeDecaissement
        fields = [
            'id', 'nom', 'type_decaissement', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# =========================
# Serializer DemandeDecaissement
# =========================
class DemandeDecaissementSerializer(serializers.ModelSerializer):
    type_decaissement = TypeDecaissementSerializer(read_only=True)
    type_decaissement_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeDecaissement.objects.all(),
        source='type_decaissement',
        write_only=True
    )

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id', 'numero', 'type_decaissement', 'type_decaissement_id',
            'demandeur_finance_id', 'validateur_coordinateur_id',
            'montant_demande', 'justification', 'statut',
            'date_demande', 'date_validation', 'commentaire_validation',
            'demande_rh_id', 'demande_stock_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'numero', 'date_demande', 'date_validation', 'created_at', 'updated_at']


# =========================
# Serializer Depense
# =========================
class DepenseSerializer(serializers.ModelSerializer):
    type_depense = TypeDecaissementSerializer(read_only=True)
    type_depense_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeDecaissement.objects.all(),
        source='type_depense',
        write_only=True
    )
    demande_decaissement = DemandeDecaissementSerializer(read_only=True)
    demande_decaissement_id = serializers.PrimaryKeyRelatedField(
        queryset=DemandeDecaissement.objects.all(),
        source='demande_decaissement',
        write_only=True
    )

    class Meta:
        model = Depense
        fields = [
            'id', 'numero', 'demande_decaissement', 'demande_decaissement_id',
            'type_depense', 'type_depense_id', 'montant', 'description', 'statut',
            'employer_id', 'demande_rh_id', 'demande_stock_id',
            'date_creation', 'date_paiement', 'responsable_finance_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'numero', 'date_creation', 'date_paiement', 'created_at', 'updated_at']


# =========================
# Serializer BulletinPaie
# =========================
class BulletinPaieSerializer(serializers.ModelSerializer):
    depense = DepenseSerializer(read_only=True)
    depense_id = serializers.PrimaryKeyRelatedField(
        queryset=Depense.objects.all(),
        source='depense',
        write_only=True
    )

    class Meta:
        model = BulletinPaie
        fields = [
            'id', 'numero', 'employer_id', 'depense', 'depense_id',
            'mois', 'annee', 'salaire_base', 'primes', 'retenues', 'salaire_net',
            'statut', 'date_generation', 'date_validation',
            'responsable_finance_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'numero', 'salaire_net', 'date_generation', 'date_validation', 'created_at', 'updated_at']


# =========================
# Serializer ValidationDemande
# =========================
class ValidationDemandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationDemande
        fields = [
            'id', 'numero', 'type_demande', 'demande_origine_id', 'service_origine',
            'montant', 'description', 'statut', 'validateur_finance_id',
            'date_reception', 'date_validation', 'commentaire_validation',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'numero', 'date_reception', 'date_validation', 'created_at', 'updated_at']
