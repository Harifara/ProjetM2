import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# =====================================
# Demande de Décaissement (Finance → Coordo)
# =====================================
class DemandeDecaissement(models.Model):
    STATUS_CHOICES = [
        ('non_envoyee', 'Non envoyée'),
        ('en_attente', 'Envoyée au Coordonnateur'),
        ('partiellement_valide', 'Partiellement validée'),
        ('valide', 'Validée'),
        ('rejete', 'Rejetée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_service = models.CharField(max_length=50)  # RH ou Stock
    created_by = models.UUIDField()  # UUID du responsable finance
    date_creation = models.DateTimeField(auto_now_add=True)
    envoyee = models.BooleanField(default=False)  # Envoyée au Coordonnateur
    total_montant = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    @property
    def statut(self):
        if not self.envoyee:
            return 'non_envoyee'
        dep_status = set(dep.statut for dep in self.depenses.all())
        if not dep_status:
            return 'en_attente'
        elif dep_status == {'valide'}:
            return 'valide'
        elif 'valide' in dep_status:
            return 'partiellement_valide'
        elif dep_status == {'rejete'}:
            return 'rejete'
        else:
            return 'en_attente'

    def calculer_total(self):
        self.total_montant = sum(dep.montant for dep in self.depenses.all())
        self.save()


# =====================================
# Dépense (Article ou paiement lié à la demande)
# =====================================
class Depense(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé par Coordonnateur'),
        ('rejete', 'Rejeté par Coordonnateur'),
        ('paye', 'Payé'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    demande = models.ForeignKey(DemandeDecaissement, on_delete=models.CASCADE, related_name='depenses')
    description = models.TextField()
    montant = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.01)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)


# =====================================
# Dépense Finale (Créée automatiquement après validation Coordo)
# =====================================
class DepenseFinale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    depense = models.OneToOneField(Depense, on_delete=models.CASCADE, related_name='depense_finale')
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    paye = models.BooleanField(default=False)


# =====================================
# Signal : créer une dépense finale dès qu'une dépense est validée
# =====================================
@receiver(post_save, sender=Depense)
def create_depense_finale(sender, instance, **kwargs):
    if instance.statut == 'valide' and not hasattr(instance, 'depense_finale'):
        DepenseFinale.objects.create(depense=instance, montant=instance.montant)
        if instance.demande:
            instance.demande.calculer_total()
