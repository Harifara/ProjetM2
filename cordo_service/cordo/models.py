import uuid
from django.db import models
from django.utils import timezone

class ValidationCoordonnateur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    demande_decaissement_id = models.UUIDField(unique=True)
    coordonnateur_id = models.UUIDField()
    decision = models.CharField(max_length=20)
    commentaire = models.TextField(blank=True)
    date_validation = models.DateTimeField(default=timezone.now)
