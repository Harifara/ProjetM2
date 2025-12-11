# finance/serializers.py
from rest_framework import serializers
from .models import DemandeDecaissement, Depense, DepenseFinale
from django.conf import settings
import requests


class DepenseFinaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepenseFinale
        fields = ["id", "montant", "date_creation", "paye"]


class DepenseSerializer(serializers.ModelSerializer):
    depense_finale = DepenseFinaleSerializer(read_only=True)

    class Meta:
        model = Depense
        fields = [
            "id", "demande", "description", "montant",
            "statut", "date_creation", "depense_finale"
        ]
        read_only_fields = ["id", "date_creation", "depense_finale"]


class DemandeDecaissementSerializer(serializers.ModelSerializer):
    depenses = DepenseSerializer(many=True, read_only=True)
    statut = serializers.CharField(read_only=True)

    # Détails RH / STOCK depuis microservices (read-only)
    rh_details = serializers.SerializerMethodField()
    stock_details = serializers.SerializerMethodField()

    class Meta:
        model = DemandeDecaissement
        fields = [
            "id", "source_service", "created_by", "date_creation",
            "demande_id", "demandeAchat_id", "envoyee",
            "coordo_decision", "coordo_id", "coordo_date", "coordo_commentaire",
            "total_montant", "statut", "rh_details", "stock_details", "depenses"
        ]
        read_only_fields = [
            "id", "date_creation", "total_montant", "statut",
            "coordo_decision", "coordo_id", "coordo_date"
        ]

    def get_rh_details(self, obj):
        if not obj.demande_id:
            return None
        try:
            r = requests.get(f"{settings.RH_SERVICE_URL}/api/demandes/{obj.demande_id}/")
            return r.json() if r.status_code == 200 else {"error": "Introuvable dans RH"}
        except requests.exceptions.RequestException:
            return {"error": "Connexion impossible à RH"}

    def get_stock_details(self, obj):
        if not obj.demandeAchat_id:
            return None
        try:
            r = requests.get(f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/{obj.demandeAchat_id}/")
            return r.json() if r.status_code == 200 else {"error": "Introuvable dans STOCK"}
        except requests.exceptions.RequestException:
            return {"error": "Connexion impossible à STOCK"}
