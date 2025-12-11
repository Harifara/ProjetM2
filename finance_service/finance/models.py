# finance/models.py
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class DemandeDecaissement(models.Model):
    STATUS_CHOICES = [
        ('non_envoyee', 'Non envoyée'),
        ('en_attente', 'Envoyée au Coordonnateur'),
        ('partiellement_valide', 'Partiellement validée'),
        ('valide', 'Validée'),
        ('rejete', 'Rejetée'),
    ]

    COORDO_DECISION_CHOICES = [
        ('non_traite', 'Non traité'),
        ('valide', 'Validé par coordo'),
        ('rejete', 'Rejeté par coordo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_service = models.CharField(max_length=50)  # 'RH' ou 'STOCK'
    created_by = models.UUIDField()  # UUID du responsable finance
    date_creation = models.DateTimeField(auto_now_add=True)

    # Liens éventuels vers RH / STOCK
    demande_id = models.UUIDField(null=True, blank=True)
    demandeAchat_id = models.UUIDField(null=True, blank=True)

    # Envoi au coordo
    envoyee = models.BooleanField(default=False)

    # Décision du coordonnateur
    coordo_decision = models.CharField(max_length=20, choices=COORDO_DECISION_CHOICES, default='non_traite')
    coordo_id = models.UUIDField(null=True, blank=True)
    coordo_date = models.DateTimeField(null=True, blank=True)
    coordo_commentaire = models.TextField(blank=True)

    total_montant = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        label = "RH" if self.demande_id else ("STOCK" if self.demandeAchat_id else "GEN")
        return f"Décaissement ({label}) - {self.id}"

    @property
    def statut(self):
        """
        Statut calculé :
        - non_envoyee : pas encore envoyé au coordo
        - en_attente : envoyé mais non traité par coordo
        - valide / partiellement_valide / rejete : selon décisions et dépenses
        """
        if not self.envoyee:
            return 'non_envoyee'

        if self.coordo_decision == 'non_traite':
            return 'en_attente'

        if self.coordo_decision == 'rejete':
            return 'rejete'

        # Si coordo a validé, regarder les dépenses
        statuses = set(dep.statut for dep in self.depenses.all())

        if not statuses:
            return 'en_attente'

        if statuses == {'valide'}:
            return 'valide'

        if 'valide' in statuses:
            return 'partiellement_valide'

        if statuses == {'rejete'}:
            return 'rejete'

        return 'en_attente'

    def calculer_total(self):
        """Recalculer total_montant depuis les dépenses existantes."""
        total = sum((dep.montant for dep in self.depenses.all()), Decimal('0.00'))
        self.total_montant = total
        self.save(update_fields=['total_montant'])


class Depense(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('paye', 'Payé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    demande = models.ForeignKey(DemandeDecaissement, on_delete=models.CASCADE, related_name='depenses')
    description = models.TextField()
    montant = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} ({self.montant})"


class DepenseFinale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    depense = models.OneToOneField(Depense, on_delete=models.CASCADE, related_name='depense_finale')
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    paye = models.BooleanField(default=False)

    def __str__(self):
        return f"Finale {self.depense_id} - {self.montant}"


# Signal : créer automatiquement une DepenseFinale si dépense validée
@receiver(post_save, sender=Depense)
def create_depense_finale(sender, instance: Depense, created, **kwargs):
    if instance.statut == 'valide':
        if not hasattr(instance, 'depense_finale'):
            DepenseFinale.objects.create(depense=instance, montant=instance.montant)

    if instance.demande:
        instance.demande.calculer_total()
