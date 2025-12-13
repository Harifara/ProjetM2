# finance/models.py
import uuid
from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError


class DemandeDecaissement(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('en_attente_coordonnateur', 'En attente validation coordonnateur'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('decaisse', 'Décaissement effectué'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=20, unique=True, blank=True)
    # Références externes (microservices)
    demandes_rh_ids = models.JSONField(default=list, blank=True)
    demandes_stock_ids = models.JSONField(default=list, blank=True)

    montant_total = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )

    statut = models.CharField(
        max_length=30, choices=STATUT_CHOICES, default='brouillon'
    )

    cree_par_id = models.UUIDField(help_text="UUID utilisateur finance")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_decaissement = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Décaissement {self.reference or self.id} | {self.statut}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            # Exemple : DEC-20251213-001 (date + auto-increment)
            last = DemandeDecaissement.objects.filter(date_creation__date=self.date_creation.date()).count() + 1
            self.reference = f"DEC-{self.date_creation:%Y%m%d}-{last:03d}"
        super().save(*args, **kwargs)

    # ------------------------
    # Méthodes métier
    # ------------------------
    def calculer_montant_total(self, montant_rh=0, montant_stock=0):
        self.montant_total = Decimal(montant_rh) + Decimal(montant_stock)
        self.save()

    def soumettre_coordonnateur(self):
        if self.statut != 'brouillon':
            raise ValidationError("Seules les demandes en brouillon peuvent être soumises.")
        self.statut = 'en_attente_coordonnateur'
        self.save()

    def approuver(self):
        self.statut = 'approuve'
        self.save()

    def rejeter(self):
        self.statut = 'rejete'
        self.save()

    def marquer_decaisse(self):
        if self.statut != 'approuve':
            raise ValidationError("Décaissement autorisé uniquement après approbation.")
        self.statut = 'decaisse'
        self.date_decaissement = timezone.now()
        self.save()


class Depense(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ('espece', 'Espèce'),
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('mobile_money', 'Mobile Money'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    decaissement = models.ForeignKey(
        DemandeDecaissement,
        on_delete=models.PROTECT,
        related_name='depenses'
    )

    montant = models.DecimalField(max_digits=15, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES)
    reference = models.CharField(max_length=255, blank=True)

    paye_par_id = models.UUIDField(help_text="UUID agent finance")
    date_depense = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_depense']

    def __str__(self):
        return f"Dépense {self.id} | {self.montant}"

    @staticmethod
    def lister_depenses(decaissement_id):
        return Depense.objects.filter(decaissement_id=decaissement_id)
