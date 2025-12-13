from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
import logging

from .models import ValidationCoordonnateur
from .serializers import ValidationCoordonnateurSerializer, ValidationCoordonnateurCreateSerializer

logger = logging.getLogger(__name__)

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
        finance_status = "non testé"
        try:
            response = requests.post(
                f"{settings.FINANCE_SERVICE_URL}/api/decaissements/{validation.demande_decaissement_id}/decision/",
                json={
                    "decision": validation.decision,
                    "commentaire": validation.commentaire,
                    # ajouter ici les champs nécessaires attendus par Finance, ex: "coordonnateur_id": validation.coordonnateur_id
                },
                timeout=5
            )
            response.raise_for_status()
            finance_status = "succès"
        except requests.RequestException as e:
            if e.response is not None:
                logger.error(f"Erreur service Finance: {e.response.status_code} {e.response.text}")
                finance_status = f"échec: {e.response.status_code} {e.response.text}"
            else:
                logger.error(f"Erreur service Finance: {str(e)}")
                finance_status = f"échec: {str(e)}"

        return Response(
            {
                "validation": ValidationCoordonnateurSerializer(validation).data,
                "finance_status": finance_status
            },
            status=status.HTTP_201_CREATED
        )
