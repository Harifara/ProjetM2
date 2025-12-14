from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
from .models import ValidationCoordonnateur
from .serializers import ValidationCoordonnateurSerializer, ValidationCoordonnateurCreateSerializer

class ValidationCoordonnateurViewSet(viewsets.ModelViewSet):
    queryset=ValidationCoordonnateur.objects.all()
    permission_classes=[IsAuthenticated]

    def get_serializer_class(self):
        return ValidationCoordonnateurCreateSerializer if self.action=='create' else ValidationCoordonnateurSerializer

    def perform_create(self, serializer):
        validation=serializer.save()
        # notifier finance
        requests.post(
            f"{settings.FINANCE_SERVICE_URL}/api/coordonnateur/decaissements/{validation.demande_decaissement_id}/decision/",
            json={"decision": validation.decision},
            timeout=5
        )
