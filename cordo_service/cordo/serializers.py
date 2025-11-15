from rest_framework import serializers
from .models import (
    ProfilCoordinateur,
    DossierDecaissement,
    HistoriqueValidation,
    StatistiquesValidation,
    ModeleDecision,
    AlerteDecaissement,
    Vue_DemandesPendantes
)

# ============================================================
# HistoriqueValidation Serializer
# ============================================================
class HistoriqueValidationSerializer(serializers.ModelSerializer):
    coordinateur = serializers.StringRelatedField(read_only=True)  # Nom complet du coordinateur
    coordinateur_id = serializers.UUIDField(write_only=True)
    dossier_decaissement_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = HistoriqueValidation
        fields = '__all__'
        read_only_fields = ['id', 'date_validation', 'created_at']

# ============================================================
# AlerteDecaissement Serializer
# ============================================================
class AlerteDecaissementSerializer(serializers.ModelSerializer):
    dossier_decaissement_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = AlerteDecaissement
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'lue_le']

# ============================================================
# DossierDecaissement Serializer
# ============================================================
class DossierDecaissementSerializer(serializers.ModelSerializer):
    coordinateur = serializers.StringRelatedField(read_only=True)
    coordinateur_id = serializers.UUIDField(write_only=True)
    
    historique_validations = HistoriqueValidationSerializer(many=True, read_only=True)
    alertes = AlerteDecaissementSerializer(many=True, read_only=True)

    class Meta:
        model = DossierDecaissement
        fields = '__all__'
        read_only_fields = ['id', 'numero', 'date_reception', 'created_at', 'updated_at']

# ============================================================
# StatistiquesValidation Serializer
# ============================================================
class StatistiquesValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatistiquesValidation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# ============================================================
# ProfilCoordinateur Serializer complet
# ============================================================
class ProfilCoordinateurSerializer(serializers.ModelSerializer):
    dossiers_decaissement = DossierDecaissementSerializer(many=True, read_only=True)
    validations_effectuees = HistoriqueValidationSerializer(many=True, read_only=True)
    statistiques = StatistiquesValidationSerializer(read_only=True)

    class Meta:
        model = ProfilCoordinateur
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# ============================================================
# ModeleDecision Serializer
# ============================================================
class ModeleDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeleDecision
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# ============================================================
# Vue_DemandesPendantes Serializer (read-only view)
# ============================================================
class VueDemandesPendantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vue_DemandesPendantes
        fields = '__all__'
        read_only_fields = '__all__'
