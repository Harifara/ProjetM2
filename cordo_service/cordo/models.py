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
    demande_decaissement_id = models.UUIDField(unique=True)
    coordonnateur_id = models.UUIDField()
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    commentaire = models.TextField(blank=True)
    date_validation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_validation']
        db_table = 'validations_coordonnateur'

    def __str__(self):
        return f"{self.demande_decaissement_id} → {self.decision}"
