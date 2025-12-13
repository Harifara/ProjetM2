# coordonnateur/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings

from .models import ValidationCoordonnateur
from .serializers import (
    ValidationCoordonnateurSerializer,
    ValidationCoordonnateurCreateSerializer,
)


class ValidationCoordonnateurViewSet(viewsets.ModelViewSet):
    queryset = ValidationCoordonnateur.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ValidationCoordonnateurCreateSerializer
        return ValidationCoordonnateurSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        validation = serializer.save()

        # Appel service Finance
        try:
            response = requests.post(
                f"{settings.FINANCE_SERVICE_URL}/api/decaissements/"
                f"{validation.demande_decaissement_id}/decision/",
                json={
                    "decision": validation.decision,
                    "commentaire": validation.commentaire,
                },
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException:
            pass  # Log uniquement, ne bloque pas la création locale

        return Response(
            ValidationCoordonnateurSerializer(validation).data,
            status=status.HTTP_201_CREATED
        )
