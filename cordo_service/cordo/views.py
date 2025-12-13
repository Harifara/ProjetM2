from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
import logging

from .models import ValidationCoordonnateur
from .serializers import ValidationCoordonnateurSerializer

logger = logging.getLogger(__name__)

class ValidationCoordonnateurViewSet(viewsets.ModelViewSet):
    queryset = ValidationCoordonnateur.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            from .serializers import ValidationCoordonnateurCreateSerializer
            return ValidationCoordonnateurCreateSerializer
        return ValidationCoordonnateurSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Crée ou met à jour la validation pour éviter les doublons
        validation, created = ValidationCoordonnateur.objects.update_or_create(
            demande_decaissement_id=data['demande_decaissement_id'],
            defaults={
                'coordonnateur_id': request.user.id,
                'decision': data['decision'],
                'commentaire': data.get('commentaire', ''),
            }
        )

        # Appel service Finance
        finance_status = "non testé"
        updated_decaissement = None
        try:
            response = requests.post(
                f"{settings.FINANCE_SERVICE_URL}/api/decaissements/{validation.demande_decaissement_id}/decision/",
                json={
                    "decision": validation.decision,
                    "commentaire": validation.commentaire,
                    "coordonnateur_id": validation.coordonnateur_id,  # si requis par Finance
                },
                timeout=5
            )
            response.raise_for_status()
            finance_status = "succès"
            updated_decaissement = response.json()  # décaissement avec statut mis à jour
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
                "finance_status": finance_status,
                "decaissement": updated_decaissement
            },
            status=status.HTTP_201_CREATED
        )
