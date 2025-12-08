from django.db import models
import uuid
from django.utils import timezone
import requests
from django.conf import settings

class ValidationCoordinateur(models.Model):
    STATUS_CHOICES = [
        ('approuve', 'Approuvé'),
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

    def enregistrer_validation(self):
        """
        Enregistre la validation côté coordinateur et notifie finance_service
        pour mettre à jour le statut de l'item et recalculer le statut global.
        """
        # URL de l'API de finance_service pour mettre à jour un item décaissement
        finance_api_url = f"{settings.FINANCE_SERVICE_URL}/api/decaissements/items/{self.item_decaissement_id}/validation/"

        payload = {
            "statut": "valide" if self.statut == "approuve" else "rejete",
            "coordinateur_id": str(self.coordinateur_id),
            "commentaire": self.commentaire,
        }

        try:
            response = requests.post(finance_api_url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            # Log l'erreur et laisse la validation enregistrée localement
            print(f"Erreur lors de la mise à jour sur finance_service : {e}")

        # Sauvegarde locale de la validation
        self.save()
