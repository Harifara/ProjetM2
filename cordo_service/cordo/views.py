from rest_framework import viewsets
from .models import ValidationCoordinateur
from .serializers import ValidationCoordinateurSerializer

class ValidationCoordinateurViewSet(viewsets.ModelViewSet):
    queryset = ValidationCoordinateur.objects.all()
    serializer_class = ValidationCoordinateurSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validation = serializer.save()
        # Appliquer la validation sur l'item et mettre à jour le statut global
        validation.enregistrer_validation()
        return Response(serializer.data, status=201)
