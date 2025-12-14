# coordonnateur/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from django.conf import settings
from .models import ValidationCoordonnateur
from .serializers import (
    ValidationCoordonnateurSerializer,
    ValidationCoordonnateurCreateSerializer
)

class ValidationCoordonnateurViewSet(viewsets.ModelViewSet):
    queryset = ValidationCoordonnateur.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ValidationCoordonnateurCreateSerializer
        return ValidationCoordonnateurSerializer

    def perform_create(self, serializer):
        validation = serializer.save()

        # 🔹 Notifier le service Finance
        try:
            requests.post(
                f"{settings.FINANCE_SERVICE_URL}/api/finance/decaissements/"
                f"{validation.demande_decaissement_id}/decision/",
                json={
                    "decision": validation.decision,
                    "commentaire": validation.commentaire,
                },
                timeout=5
            )
        except requests.RequestException as e:
            # ⚠️ Log uniquement, pas de rollback
            print(f"[Coordonnateur] Erreur notification finance: {e}")
