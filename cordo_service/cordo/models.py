from django.db import models
import uuid
from django.utils import timezone

class ValidationCoordinateur(models.Model):
    STATUS_CHOICES = [
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_decaissement_id = models.UUIDField(help_text="UUID de l'item décaissement dans finance_service")
    coordinateur_id = models.UUIDField(help_text="UUID de l'utilisateur coordinateur")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES)
    commentaire = models.TextField(blank=True)
    date_validation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_validation']

    def __str__(self):
        return f"Validation {self.item_decaissement_id} - {self.statut}"

    def enregistrer_local(self):
        """
        Sauvegarde locale de la validation côté coordinateur.
        L'envoi à Finance pour mise à jour de l'item doit se faire via view ou tâche asynchrone.
        """
        self.save()
