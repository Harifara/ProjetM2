# finance/models.py

import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from rh.models import Demande as DemandeRH
from stock.models import DemandeAchat


# ======================================================
# 1) Demande de Décaissement
# ======================================================
class DemandeDecaissement(models.Model):

    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation coordinateur'),
        ('valide', 'Validé par le coordinateur'),
        ('rejete', 'Rejeté par le coordinateur'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=100, unique=True)

    # Regroupement des demandes RH
    demandes_rh = models.ManyToManyField(
        DemandeRH, related_name='decaissements', blank=True
    )

    # Regroupement des demandes Stock
    demandes_stock = models.ManyToManyField(
        DemandeAchat, related_name='decaissements', blank=True
    )

    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='en_attente'
    )

    # Créateur (Finance)
    finance_createur_id = models.UUIDField(help_text="UUID du responsable finance")

    # Decision du coordinateur
    coordinateur_valideur_id = models.UUIDField(null=True, blank=True)
    date_decision = models.DateTimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_decaissement'
        ordering = ['-created_at']
        verbose_name = "Demande de Décaissement"
        verbose_name_plural = "Demandes de Décaissement"

    # ---------------------------------
    # Calcul du montant total
    # ---------------------------------
    def recalculer_total(self):
        total_rh = sum(d.montant_total() for d in self.demandes_rh.all())
        total_stock = sum(d.montant_estime for d in self.demandes_stock.all())
        self.montant_total = total_rh + total_stock
        self.save()
        return self.montant_total

    # ---------------------------------
    # Validation par le coordinateur
    # ---------------------------------
    def valider_par_coordonateur(self, coordo_id: uuid.UUID):
        if self.statut != 'en_attente':
            raise ValidationError("Décision déjà enregistrée.")

        self.statut = 'valide'
        self.coordinateur_valideur_id = coordo_id
        self.date_decision = timezone.now()
        self.save()

        # Création automatique d'une dépense
        Depense.objects.create(
            decaissement=self,
            montant=self.montant_total,
            description=f"Dépense générée automatiquement pour {self.numero}"
        )

    def rejeter_par_coordonateur(self, coordo_id: uuid.UUID, commentaire: str = ''):
        if self.statut != 'en_attente':
            raise ValidationError("Décision déjà enregistrée.")

        self.statut = 'rejete'
        self.coordinateur_valideur_id = coordo_id
        self.commentaire = commentaire
        self.date_decision = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.numero} | Statut: {self.statut}"


# ======================================================
# 2) Dépenses générées après validation
# ======================================================
class Depense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    decaissement = models.ForeignKey(
        DemandeDecaissement,
        on_delete=models.CASCADE,
        related_name='depenses'
    )

    montant = models.DecimalField(max_digits=15, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "finance_depenses"
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Dépense {self.montant} Ar | DC {self.decaissement.numero}"
