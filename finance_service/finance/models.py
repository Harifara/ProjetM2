# finance/models.py
import uuid
from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import requests
from .utils import generate_service_token


class DemandeDecaissement(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('en_attente_coordonnateur', 'En attente coordonnateur'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('decaisse', 'Décaissé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=30, unique=True, blank=True)
    demandes_rh_ids = models.JSONField(default=list, null=True, blank=True)
    demandes_stock_ids = models.JSONField(default=list, null=True, blank=True)
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_decaissement = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.reference} | {self.montant_total} Ar"

    # ------------------------------
    # Gestion des montants
    # ------------------------------
    def recalculer_montant_total(self):
        total = 0

        token = generate_service_token()
        headers = {"Authorization": f"Bearer {token}"}

        for rh_id in self.demandes_rh_ids:
            try:
                resp = requests.get(
                    f"{settings.RH_SERVICE_URL}/api/rh/demandes/{rh_id}/",
                    headers=headers,
                    timeout=5
                )
                resp.raise_for_status()
                montant = float(resp.json().get("montant_total", 0))
                total += montant
            except requests.RequestException as e:
                print(f"[Finance] RH indisponible pour {rh_id}: {e}")

        for stock_id in self.demandes_stock_ids:
            try:
                resp = requests.get(
                    f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/{stock_id}/",
                    headers=headers,
                    timeout=5
                )
                resp.raise_for_status()
                montant = float(resp.json().get("montant_estime", 0))
                total += montant
            except requests.RequestException as e:
                print(f"[Finance] Stock indisponible pour {stock_id}: {e}")

        self.montant_total = total


    # ------------------------------
    # Vérification des demandes déjà utilisées
    # ------------------------------
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

    # ------------------------------
    # Save / création
    # ------------------------------
    def save(self, *args, **kwargs):
        creating = self._state.adding

        self.full_clean()

        if creating:
            self.recalculer_montant_total()

        if not self.reference:
            from django.db import IntegrityError

            for _ in range(5):  # retry en cas de collision
                try:
                    with transaction.atomic():
                        today = timezone.now()
                        prefix = f"DEC-{today:%Y%m%d}"

                        last = (
                            DemandeDecaissement.objects
                            .filter(reference__startswith=prefix)
                            .order_by("-reference")
                            .first()
                        )

                        if last:
                            last_num = int(last.reference.split("-")[-1])
                            next_num = last_num + 1
                        else:
                            next_num = 1

                        self.reference = f"{prefix}-{next_num:03d}"
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    continue

            raise IntegrityError("Impossible de générer une référence unique")

        super().save(*args, **kwargs)


    # ------------------------------
    # Synchronisation RH / Stock
    # ------------------------------
    def synchroniser_status(self):
        status_map = {
        'brouillon': 'en_decaissement',
        'en_attente_coordonnateur': 'en_decaissement',
        'approuve': 'valide',
        'rejete': 'refuse',
        'decaisse': 'decaisse',
    }

    mapped_status = status_map.get(self.statut, 'en_decaissement')
    token = generate_service_token()
    headers = {"Authorization": f"Bearer {token}"}

    for rh_id in self.demandes_rh_ids:
        try:
            requests.post(
                f"{settings.RH_SERVICE_URL}/api/rh/demandes/{rh_id}/update-status/",
                json={"status": mapped_status},
                headers=headers,
                timeout=5
            )
        except requests.RequestException as e:
            print(f"[Finance] Impossible de synchroniser RH {rh_id}: {e}")

    for stock_id in self.demandes_stock_ids:
        try:
            requests.post(
                f"{settings.STOCK_SERVICE_URL}/api/stock/demandes-achat/{stock_id}/update-status/",
                json={"statut": mapped_status},
                headers=headers,
                timeout=5
            )
        except requests.RequestException as e:
            print(f"[Finance] Impossible de synchroniser Stock {stock_id}: {e}")


    # ------------------------------
    # Actions
    # ------------------------------
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

    # ------------------------------
    # Filtrage des demandes reçues
    # ------------------------------
    @classmethod
    def demandes_recues(cls):
        """
        Retourne toutes les demandes qui ne sont pas encore en décaissement.
        """
        return cls.objects.exclude(statut='en_decaissement').order_by('-date_creation')


# ------------------------------
# Dépenses liées
# ------------------------------
class Depense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decaissement = models.ForeignKey(DemandeDecaissement, on_delete=models.PROTECT, related_name='depenses')
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    mode_paiement = models.CharField(max_length=20)
    paye_par_id = models.UUIDField()
    date_depense = models.DateTimeField(default=timezone.now)
