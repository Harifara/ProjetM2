# finance/serializers.py
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
        ]
        read_only_fields = ["montant_total", "date_creation", "depenses"]

    def create(self, validated_data):
        """
        Création d'une demande de décaissement avec recalcul automatique des montants
        et synchronisation des statuts RH et Stock.
        """
        demandes_rh_ids = validated_data.get("demandes_rh_ids", [])
        demandes_stock_ids = validated_data.get("demandes_stock_ids", [])
        user_id = validated_data.get("cree_par_id")
        
        decaissement = DemandeDecaissement(
            demandes_rh_ids=demandes_rh_ids,
            demandes_stock_ids=demandes_stock_ids,
            cree_par_id=user_id
        )
        decaissement.save()
        decaissement.synchroniser_status()
        return decaissement

    def update(self, instance, validated_data):
        """
        Mise à jour d'une demande de décaissement et synchronisation des statuts.
        """
        instance.statut = validated_data.get("statut", instance.statut)
        instance.save()
        instance.synchroniser_status()
        return instance
