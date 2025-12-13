from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import ValidationCoordonnateur
from .serializers import (
    ValidationCoordonnateurSerializer,
    ValidationCoordonnateurCreateSerializer,
)


class ValidationCoordonnateurViewSet(viewsets.ModelViewSet):
    queryset = ValidationCoordonnateur.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ValidationCoordonnateurCreateSerializer
        return ValidationCoordonnateurSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validation = serializer.save()

        # ============================
        # APPEL INTER-SERVICE FINANCE
        # ============================
        # À remplacer par ton client HTTP réel (requests / httpx)
        #
        # finance_api.update_statut_decaissement(
        #     decaissement_id=validation.demande_decaissement_id,
        #     decision=validation.decision
        # )

        return Response(
            ValidationCoordonnateurSerializer(validation).data,
            status=status.HTTP_201_CREATED
        )


