from rest_framework import serializers
from .models import DemandeDecaissement, Depense
from rh.models import Demande as DemandeRH
from stock.models import DemandeAchat


# -------------------------------------------------------------------
# SERIALIZERS DES DEMANDES RH ET STOCK (lecture seule dans finance)
# -------------------------------------------------------------------
class DemandeRHSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeRH
        fields = ['id', 'description', 'status', 'montant_total', 'date_demande']
        read_only_fields = fields


class DemandeAchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeAchat
        fields = [
            'id', 'numero', 'article', 'quantite',
            'montant_estime', 'statut', 'statut_reception',
            'created_at'
        ]
        read_only_fields = fields


# -------------------------------------------------------------------
# DEPENSE (générée automatiquement)
# -------------------------------------------------------------------
class DepenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depense
        fields = [
            'id',
            'decaissement',
            'montant',
            'date_paiement',
            'description',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'date_paiement']


# -------------------------------------------------------------------
# DEMANDE DE DÉCAISSEMENT — LISTE
# -------------------------------------------------------------------
class DemandeDecaissementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'numero',
            'montant_total',
            'statut',
            'finance_createur_id',
            'coordinateur_valideur_id',
            'date_decision',
            'created_at'
        ]
        read_only_fields = fields


# -------------------------------------------------------------------
# DEMANDE DE DÉCAISSEMENT — DÉTAIL COMPLET
# -------------------------------------------------------------------
class DemandeDecaissementDetailSerializer(serializers.ModelSerializer):
    demandes_rh = DemandeRHSerializer(many=True, read_only=True)
    demandes_stock = DemandeAchatSerializer(many=True, read_only=True)
    depenses = DepenseSerializer(many=True, read_only=True)

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'numero',
            'demandes_rh',
            'demandes_stock',
            'montant_total',
            'statut',
            'finance_createur_id',
            'coordinateur_valideur_id',
            'date_decision',
            'commentaire',
            'depenses',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'montant_total', 'statut', 'coordinateur_valideur_id',
            'date_decision', 'depenses', 'created_at', 'updated_at'
        ]


# -------------------------------------------------------------------
# DEMANDE DE DÉCAISSEMENT — CRÉATION / UPDATE
# -------------------------------------------------------------------
class DemandeDecaissementCreateSerializer(serializers.ModelSerializer):
    demandes_rh_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True
    )
    demandes_stock_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = DemandeDecaissement
        fields = [
            'id',
            'numero',
            'finance_createur_id',
            'demandes_rh_ids',
            'demandes_stock_ids'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        rh_ids = validated_data.pop('demandes_rh_ids', [])
        stock_ids = validated_data.pop('demandes_stock_ids', [])

        decaissement = DemandeDecaissement.objects.create(**validated_data)

        # Attach RH
        if rh_ids:
            demandes_rh = DemandeRH.objects.filter(id__in=rh_ids)
            decaissement.demandes_rh.set(demandes_rh)

        # Attach Stock
        if stock_ids:
            demandes_stock = DemandeAchat.objects.filter(id__in=stock_ids)
            decaissement.demandes_stock.set(demandes_stock)

        # Recalculer total
        decaissement.recalculer_total()
        return decaissement

    def update(self, instance, validated_data):
        rh_ids = validated_data.pop('demandes_rh_ids', None)
        stock_ids = validated_data.pop('demandes_stock_ids', None)

        instance.numero = validated_data.get('numero', instance.numero)
        instance.finance_createur_id = validated_data.get('finance_createur_id', instance.finance_createur_id)
        instance.save(update_fields=['numero', 'finance_createur_id'])

        # Update RH
        if rh_ids is not None:
            demandes_rh = DemandeRH.objects.filter(id__in=rh_ids)
            instance.demandes_rh.set(demandes_rh)

        # Update Stock
        if stock_ids is not None:
            demandes_stock = DemandeAchat.objects.filter(id__in=stock_ids)
            instance.demandes_stock.set(demandes_stock)

        # Recalculer total
        instance.recalculer_total()
        return instance
