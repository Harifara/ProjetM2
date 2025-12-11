# coordonateur/models.py

import uuid
from django.db import models
from django.utils import timezone
from finance.models import DemandeDecaissement  # ⬅️ Import depuis Finance

class ValidationCoordinateur(models.Model):
    DECISION_CHOICES = [
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Lien vers la demande de décaissement
    decaissement = models.ForeignKey(
        DemandeDecaissement,
        on_delete=models.CASCADE,
        related_name='validations'
    )

    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    commentaire = models.TextField(blank=True)

    # Optionnel : coordinateur peut être lié à un User ou juste son UUID
    coordinateur_id = models.UUIDField()
    date_decision = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'coordo_validations'
        ordering = ['-date_decision']
        verbose_name = "Validation du Coordinateur"
        verbose_name_plural = "Validations du Coordinateur"

    def __str__(self):
        return f"{self.decision.upper()} | DC {self.decaissement.id} | {self.date_decision}"
