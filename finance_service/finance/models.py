from django.db import models
import uuid
from decimal import Decimal
from django.core.validators import MinValueValidator

# =====================================
# 💰 Demande de décaissement
# =====================================
class DemandeDecaissement(models.Model):
    STATUS_CHOICES = [
        ('non_envoyee', 'Non envoyée'),
        ('en_attente', 'En attente'),
        ('partiellement_valide', 'Partiellement validée'),
        ('valide', 'Validée'),
        ('rejete', 'Rejetée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_service = models.CharField(max_length=50, help_text="RH ou Stock")
    date_creation = models.DateTimeField(auto_now_add=True)
    created_by = models.UUIDField(help_text="UUID de l'utilisateur finance/coordonnateur")
    total_montant = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    envoyee = models.BooleanField(default=False, help_text="Indique si la demande a déjà été envoyée pour décaissement")

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Décaissement {self.id} - Total: {self.total_montant}"

    @property
    def statut(self):
        """Retourne le statut calculé : 'non_envoyee' si jamais envoyée, sinon en_attente ou selon depenses."""
        if not self.envoyee:
            return 'non_envoyee'

        depenses = self.depenses.all()
        statuts = set(depense.statut for depense in depenses)

        if not statuts:
            return 'en_attente'
        elif statuts == {'valide'}:
            return 'valide'
        elif 'valide' in statuts:
            return 'partiellement_valide'
        elif statuts == {'rejete'}:
            return 'rejete'
        else:
            return 'en_attente'

    def calculer_total(self):
        total = sum((depense.montant for depense in self.depenses.all()), Decimal('0.00'))
        self.total_montant = total
        self.save()


# =====================================
# 💵 Dépenses / items liés à la demande
# =====================================
class Depense(models.Model):
    STATUS_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('paye', 'Payé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    demande = models.ForeignKey(DemandeDecaissement, on_delete=models.CASCADE, related_name='depenses')
    description = models.TextField(help_text="Article ou paiement reçu depuis RH / Stock")
    montant = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.montant} - {self.statut}"


# =====================================
# 🔔 Signal pour mise à jour automatique
# =====================================
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Depense)
def handle_depense_validation(sender, instance, **kwargs):
    # Le statut sera recalculé automatiquement via la propriété
    instance.demande.calculer_total()
