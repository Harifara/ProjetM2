# coordonnateur/models.py
import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class ValidationCoordonnateur(models.Model):
    DECISION_CHOICES = [
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    demande_decaissement_id = models.UUIDField(
        help_text="UUID de la demande de décaissement (service finance)"
    )

    coordonnateur_id = models.UUIDField(
        help_text="UUID utilisateur coordonnateur"
    )

    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    commentaire = models.TextField(blank=True)

    date_validation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_validation']
        unique_together = ('demande_decaissement_id',)

    def __str__(self):
        return f"Validation {self.demande_decaissement_id} | {self.decision}"

    # ------------------------
    # Méthodes métier
    # ------------------------
    def valider(self):
        self.decision = 'approuve'
        self.date_validation = timezone.now()
        self.save()

    def rejeter(self, commentaire=''):
        self.decision = 'rejete'
        self.commentaire = commentaire
        self.date_validation = timezone.now()
        self.save()
