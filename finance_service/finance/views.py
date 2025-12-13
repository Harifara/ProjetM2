from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DemandeDecaissement, Depense
from .serializers import (
    DepenseSerializer,
    DemandeDecaissementListSerializer,
    DemandeDecaissementDetailSerializer,
    DemandeDecaissementCreateSerializer,
    SoumettreCoordonnateurSerializer,
)


class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return DemandeDecaissementListSerializer
        if self.action == 'retrieve':
            return DemandeDecaissementDetailSerializer
        if self.action == 'create':
            return DemandeDecaissementCreateSerializer
        if self.action == 'soumettre_coordonnateur':
            return SoumettreCoordonnateurSerializer
        return DemandeDecaissementDetailSerializer

    @action(
        detail=True,
        methods=['post'],
        url_path='soumettre'
    )
    def soumettre_coordonnateur(self, request, pk=None):
        decaissement = self.get_object()

        serializer = SoumettreCoordonnateurSerializer(
            decaissement, data={}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Demande soumise au coordonnateur."},
            status=status.HTTP_200_OK
        )

class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
