from django.db import models
import uuid
from decimal import Decimal
from django.utils import timezone

class ValidationCoordinateur(models.Model):
    STATUS_CHOICES = [
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_decaissement = models.ForeignKey('finance.DemandeDecaissementItem', on_delete=models.CASCADE, related_name='validations')
    coordinateur_id = models.UUIDField(help_text="UUID de l'utilisateur coordinateur")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES)
    commentaire = models.TextField(blank=True)
    date_validation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_validation']

    def __str__(self):
        return f"Validation {self.item_decaissement.id} - {self.statut}"

    def enregistrer_validation(self):
        """Met à jour le statut de l'item décaissement et recalcul le statut global du décaissement."""
        if self.statut == 'approuve':
            self.item_decaissement.statut = 'valide'
        else:
            self.item_decaissement.statut = 'rejete'
        self.item_decaissement.save()
        # Mise à jour du statut global du décaissement
        self.item_decaissement.decaissement.mettre_a_jour_statut()
