from rest_framework import serializers
from .models import DemandeDecaissement, Depense


class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = [
            "id",
            "montant",
            "mode_paiement",
            "paye_par_id",
            "date_depense",
        ]


class DemandeDecaissementSerializer(serializers.ModelSerializer):
    depenses = DepenseSerializer(many=True, read_only=True)
    rh_details = serializers.SerializerMethodField()
    stock_details = serializers.SerializerMethodField()

    class Meta:
        model = DemandeDecaissement
        fields = [
            "id",
            "reference",
            "demandes_rh_ids",
            "demandes_stock_ids",
            "montant_total",
            "statut",
            "date_creation",
            "date_decaissement",
            "depenses",
            "rh_details",
            "stock_details",
        ]
        read_only_fields = [
            "montant_total",
            "date_creation",
            "depenses",
            "reference",
            "rh_details",
            "stock_details",
        ]

    def get_rh_details(self, obj):
        return obj.get_rh_details()  # Méthode dans le modèle pour récupérer infos RH

    def get_stock_details(self, obj):
        return obj.get_stock_details()  # Méthode dans le modèle pour récupérer infos Stock

    def create(self, validated_data):
        demandes_rh_ids = validated_data.get("demandes_rh_ids", [])
        demandes_stock_ids = validated_data.get("demandes_stock_ids", [])

        decaissement = DemandeDecaissement(
            demandes_rh_ids=demandes_rh_ids,
            demandes_stock_ids=demandes_stock_ids,
        )
        decaissement.save()
        decaissement.recalculer_montant_total()
        decaissement.save()
        decaissement.synchroniser_status()
        return decaissement

    def update(self, instance, validated_data):
        instance.statut = validated_data.get("statut", instance.statut)
        instance.demandes_rh_ids = validated_data.get("demandes_rh_ids", instance.demandes_rh_ids)
        instance.demandes_stock_ids = validated_data.get("demandes_stock_ids", instance.demandes_stock_ids)

        instance.recalculer_montant_total()
        instance.save()
        instance.synchroniser_status()
        return instance
