# finance/models.py
import uuid
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import requests

class DemandeDecaissement(models.Model):
    STATUT_CHOICES = [
        ('brouillon','Brouillon'),
        ('en_attente_coordonnateur','En attente coordonnateur'),
        ('approuve','Approuvé'),
        ('rejete','Rejeté'),
        ('decaisse','Décaissé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=30, unique=True, blank=True)
    demandes_rh_ids = models.JSONField(default=list, blank=True)
    demandes_stock_ids = models.JSONField(default=list, blank=True)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='brouillon')
    cree_par_id = models.UUIDField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_decaissement = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.reference} | {self.montant_total} Ar"

    def recalculer_montant_total(self):
        total = Decimal("0.00")
        valid_rh_ids = []
        valid_stock_ids = []

        # 🔹 Montants RH
        for rh_id in self.demandes_rh_ids:
            try:
                resp = requests.get(
                    f"{settings.RH_SERVICE_URL}/api/demandes/{rh_id}/montant/",
                    timeout=5
                )
                resp.raise_for_status()
                montant = Decimal(str(resp.json().get("montant", 0)))
                total += montant
                valid_rh_ids.append(rh_id)
            except requests.RequestException as e:
                print(f"[Finance] Impossible de récupérer le montant RH pour {rh_id}: {e}")

        # 🔹 Montants Stock
        for stock_id in self.demandes_stock_ids:
            try:
                resp = requests.get(
                    f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/{stock_id}/montant/",
                    timeout=5
                )
                resp.raise_for_status()
                montant = Decimal(str(resp.json().get("montant", 0)))
                total += montant
                valid_stock_ids.append(stock_id)
            except requests.RequestException as e:
                print(f"[Finance] Impossible de récupérer le montant Stock pour {stock_id}: {e}")

        # Mettre à jour les montants et IDs valides
        self.montant_total = total
        self.demandes_rh_ids = valid_rh_ids
        self.demandes_stock_ids = valid_stock_ids

    @classmethod
    def get_demandes_deja_utilisees(cls):
        rh_ids, stock_ids = set(), set()
        for d in cls.objects.exclude(statut='rejete'):
            rh_ids.update(d.demandes_rh_ids)
            stock_ids.update(d.demandes_stock_ids)
        return rh_ids, stock_ids

    def clean(self):
        rh_used, stock_used = self.get_demandes_deja_utilisees()
        for rh_id in self.demandes_rh_ids:
            if rh_id in rh_used and not self.pk:
                raise ValidationError(f"Demande RH déjà utilisée : {rh_id}")
        for stock_id in self.demandes_stock_ids:
            if stock_id in stock_used and not self.pk:
                raise ValidationError(f"Demande Stock déjà utilisée : {stock_id}")

    def save(self, *args, **kwargs):
        creating = self._state.adding
        self.full_clean()
        if creating:
            self.recalculer_montant_total()

        if not self.reference:
            now = timezone.now()
            with transaction.atomic():
                count = DemandeDecaissement.objects.filter(date_creation__date=now.date()).count() + 1
                self.reference = f"DEC-{now:%Y%m%d}-{count:03d}"

        super().save(*args, **kwargs)

    def synchroniser_status(self):
        status_map = {
            'brouillon':'en_cours',
            'en_attente_coordonnateur':'en_cours',
            'approuve':'approuve',
            'rejete':'refuse',
            'decaisse':'decaisse',
        }
        mapped = status_map.get(self.statut, 'en_cours')

        for rh_id in self.demandes_rh_ids:
            try:
                requests.post(
                    f"{settings.RH_SERVICE_URL}/api/demandes/{rh_id}/update-status/",
                    json={"status": mapped},
                    timeout=5
                )
            except requests.RequestException as e:
                print(f"[Finance] Impossible de synchroniser statut RH {rh_id}: {e}")

        for stock_id in self.demandes_stock_ids:
            try:
                requests.post(
                    f"{settings.STOCK_SERVICE_URL}/api/demandes-achat/{stock_id}/update-status/",
                    json={"statut": mapped},
                    timeout=5
                )
            except requests.RequestException as e:
                print(f"[Finance] Impossible de synchroniser statut Stock {stock_id}: {e}")

    def soumettre_coordonnateur(self):
        if self.statut != 'brouillon':
            raise ValidationError("Seul un brouillon peut être soumis")
        self.statut = 'en_attente_coordonnateur'
        self.save()
        self.synchroniser_status()

    def appliquer_decision_coordonnateur(self, decision):
        if self.statut != 'en_attente_coordonnateur':
            raise ValidationError("Décaissement déjà traité")
        if decision not in ['approuve', 'rejete']:
            raise ValidationError("Décision invalide")
        self.statut = decision
        self.save()
        self.synchroniser_status()

    def marquer_decaisse(self):
        if self.statut != 'approuve':
            raise ValidationError("Décaissement non approuvé")
        self.statut = 'decaisse'
        self.date_decaissement = timezone.now()
        self.save()
        self.synchroniser_status()

class Depense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decaissement = models.ForeignKey(DemandeDecaissement, on_delete=models.PROTECT, related_name='depenses')
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    mode_paiement = models.CharField(max_length=20)
    paye_par_id = models.UUIDField()
    date_depense = models.DateTimeField(default=timezone.now)
