from rest_framework import serializers
from .models import (
    ProfilCoordinateur,
    DossierDecaissement,
    HistoriqueValidation,
    AlerteDecaissement,
    StatistiquesValidation,
    ModeleDecision,
    Vue_DemandesPendantes
)

# ============================================================
# 👤 Profil Coordinateur
# ============================================================
class ProfilCoordinateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilCoordinateur
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# ============================================================
# 📋 Dossier de Décaissement
# ============================================================
class DossierDecaissementSerializer(serializers.ModelSerializer):
    coordinateur = ProfilCoordinateurSerializer(read_only=True)
    
    class Meta:
        model = DossierDecaissement
        fields = '__all__'
        read_only_fields = ['id', 'numero', 'created_at', 'updated_at', 'date_reception']

# ============================================================
# ✅ Historique des Validations
# ============================================================
class HistoriqueValidationSerializer(serializers.ModelSerializer):
    dossier_decaissement = DossierDecaissementSerializer(read_only=True)
    coordinateur = ProfilCoordinateurSerializer(read_only=True)

    class Meta:
        model = HistoriqueValidation
        fields = '__all__'
        read_only_fields = ['id', 'date_validation', 'created_at']

# ============================================================
# 🔔 Alerte Décaissement
# ============================================================
class AlerteDecaissementSerializer(serializers.ModelSerializer):
    dossier_decaissement = DossierDecaissementSerializer(read_only=True)

    class Meta:
        model = AlerteDecaissement
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'lue_le']

# ============================================================
# 📊 Statistiques Validation
# ============================================================
class StatistiquesValidationSerializer(serializers.ModelSerializer):
    coordinateur = ProfilCoordinateurSerializer(read_only=True)

    class Meta:
        model = StatistiquesValidation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# ============================================================
# 📝 Modèle de Décision
# ============================================================
class ModeleDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeleDecision
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# ============================================================
# 📋 Vue pour Tableau de Bord
# ============================================================
class VueDemandesPendantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vue_DemandesPendantes
        fields = '__all__'
