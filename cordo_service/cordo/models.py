# coordonnateur/models.py
import uuid
from django.db import models
from django.utils import timezone


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
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        null=True,
        blank=True
    )
    commentaire = models.TextField(blank=True)
    date_validation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_validation']
        constraints = [
            models.UniqueConstraint(
                fields=['demande_decaissement_id'],
                name='unique_decaissement_validation'
            )
        ]

    def __str__(self):
        return f"Validation {self.demande_decaissement_id} | {self.decision}"

    # Méthodes métier
    def valider(self):
        self.decision = 'approuve'
        self.date_validation = timezone.now()
        self.save()

    def rejeter(self, commentaire=''):
        self.decision = 'rejete'
        self.commentaire = commentaire
        self.date_validation = timezone.now()
        self.save()
