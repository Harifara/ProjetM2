from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ValidationCoordinateur
from .serializers import ValidationCoordinateurSerializer

class ValidationCoordinateurViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les validations côté coordinateur.
    """
    queryset = ValidationCoordinateur.objects.all().order_by('-date_validation')
    serializer_class = ValidationCoordinateurSerializer

    def create(self, request, *args, **kwargs):
        """
        Création d'une validation.
        On peut éventuellement notifier finance_service via un signal ou tâche async.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='par-coordinateur/(?P<coordinateur_id>[^/.]+)')
    def par_coordinateur(self, request, coordinateur_id=None):
        """
        Filtrer toutes les validations d'un coordinateur spécifique.
        """
        validations = self.queryset.filter(coordinateur_id=coordinateur_id)
        page = self.paginate_queryset(validations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(validations, many=True)
        return Response(serializer.data)
