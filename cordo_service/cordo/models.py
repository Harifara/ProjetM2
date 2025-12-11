import uuid
from django.db import models
from django.utils import timezone

class ValidationCoordonnateur(models.Model):
    DECISION_CHOICES = [
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    decaissement_id = models.UUIDField()  # ID de la demande venant du service Finance
    coordo_id = models.UUIDField()
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    commentaire = models.TextField(blank=True)
    date_decision = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Decaissement {self.decaissement_id} - {self.decision}"
