import uuid
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import requests
from django.conf import settings

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
    demandes_rh_ids = models.JSONField(default=list, blank=True)
    demandes_stock_ids = models.JSONField(default=list, blank=True)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_decaissement = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Décaissement {self.reference or self.id} | {self.statut}"

    def save(self, *args, **kwargs):
        if not self.reference:
            now = self.date_creation or timezone.now()
            with transaction.atomic():
                last_count = DemandeDecaissement.objects.filter(date_creation__date=now.date()).count() + 1
                self.reference = f"DEC-{now:%Y%m%d}-{last_count:03d}"
                while DemandeDecaissement.objects.filter(reference=self.reference).exists():
                    last_count += 1
                    self.reference = f"DEC-{now:%Y%m%d}-{last_count:03d}"
        super().save(*args, **kwargs)

    # ------------------------ API RH / STOCK ------------------------
    def update_status_rh(self, rh_id, statut):
        url = f"{settings.RH_SERVICE_URL}/api/demandes/{rh_id}/update-status/"
        try:
            requests.post(url, json={"status": statut}, timeout=5)
        except requests.RequestException:
            pass

    def update_status_stock(self, stock_id, statut):
        url = f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/{stock_id}/update-status/"
        try:
            requests.post(url, json={"statut": statut}, timeout=5)
        except requests.RequestException:
            pass

    # ------------------------ SYNCHRONISATION ------------------------
    def synchroniser_status(self):
        status_map = {
            'brouillon': 'en_cours',
            'en_attente_coordonnateur': 'en_cours',
            'approuve': 'approuve',
            'rejete': 'refuse',
            'decaisse': 'decaisse',
        }
        mapped_status = status_map.get(self.statut, 'en_cours')

        # RH
        for rh_id in self.demandes_rh_ids:
            self.update_status_rh(rh_id, mapped_status)

        # Stock
        for stock_id in self.demandes_stock_ids:
            self.update_status_stock(stock_id, mapped_status)

    # ------------------------ MÉTHODES MÉTIER ------------------------
    def soumettre_coordonnateur(self):
        if self.statut != 'brouillon':
            raise ValidationError("Seules les demandes en brouillon peuvent être soumises.")
        self.statut = 'en_attente_coordonnateur'
        self.save()
        self.synchroniser_status()

    def approuver(self):
        self.statut = 'approuve'
        self.save()
        self.synchroniser_status()

    def rejeter(self):
        self.statut = 'rejete'
        self.save()
        self.synchroniser_status()

    def marquer_decaisse(self):
        if self.statut != 'approuve':
            raise ValidationError("Décaissement autorisé uniquement après approbation.")
        self.statut = 'decaisse'
        self.date_decaissement = timezone.now()
        self.save()
        self.synchroniser_status()

    # ------------------------ DEMANDES DISPONIBLES ------------------------
    @classmethod
    def get_demandes_deja_utilisees(cls):
        rh_ids = []
        stock_ids = []

        for d in cls.objects.exclude(statut='rejete'):
            rh_ids.extend(d.demandes_rh_ids)
            stock_ids.extend(d.demandes_stock_ids)

        return set(rh_ids), set(stock_ids)



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
