from django.db import models
import uuid
from decimal import Decimal
from django.core.validators import MinValueValidator

# =====================================
# 💰 Demande de décaissement
# =====================================
class DemandeDecaissement(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('partiellement_valide', 'Partiellement validée'),
        ('valide', 'Validée'),
        ('rejete', 'Rejetée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_demande_rh_id = models.UUIDField(null=True, blank=True, help_text="UUID de la demande RH")
    source_demande_stock_id = models.UUIDField(null=True, blank=True, help_text="UUID de la demande Stock")
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    total_montant = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.UUIDField(help_text="UUID de l'utilisateur finance qui crée la demande")

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Décaissement {self.id} - Total: {self.total_montant}"

    def calculer_total(self):
        """Calcul automatique du montant total à partir des items."""
        total = sum((item.montant for item in self.items.all()), Decimal('0.00'))
        self.total_montant = total
        self.save()

    def mettre_a_jour_statut(self):
        """Mise à jour automatique du statut global selon les items."""
        items = self.items.all()
        statuts = set(item.statut for item in items)
        if statuts == {'valide'}:
            self.statut = 'valide'
        elif 'valide' in statuts:
            self.statut = 'partiellement_valide'
        elif statuts == {'rejete'}:
            self.statut = 'rejete'
        else:
            self.statut = 'en_attente'
        self.save()


# =====================================
# 📝 Items de décaissement
# =====================================
class DemandeDecaissementItem(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decaissement = models.ForeignKey(DemandeDecaissement, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    montant = models.DecimalField(
        max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')

    def __str__(self):
        return f"{self.description} - {self.montant} - {self.statut}"


# =====================================
# 💵 Dépenses liées aux items
# =====================================
class Depense(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('paye', 'Payé'),
        ('partiellement', 'Partiellement payé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_decaissement = models.OneToOneField(DemandeDecaissementItem, on_delete=models.CASCADE, related_name='depense')
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut_paiement = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')

    def __str__(self):
        return f"Dépense {self.id} - {self.montant}"


# =====================================
# 🔔 Signaux pour mise à jour automatique
# =====================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=DemandeDecaissementItem)
def update_decaissement_total(sender, instance, **kwargs):
    instance.decaissement.calculer_total()
    instance.decaissement.mettre_a_jour_statut()
