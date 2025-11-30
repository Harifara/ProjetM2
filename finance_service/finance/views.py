from uuid import UUID
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import (
    TypeDecaissement,
    DemandeDecaissement,
    Depense,
    BulletinPaie,
    ValidationDemande
)
from .serializers import (
    TypeDecaissementSerializer,
    DemandeDecaissementSerializer,
    DepenseSerializer,
    BulletinPaieSerializer,
    ValidationDemandeSerializer
)


# =======================================
# ViewSet pour TypeDecaissement
# =======================================
class TypeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = TypeDecaissement.objects.all().order_by('nom')
    serializer_class = TypeDecaissementSerializer
    permission_classes = [IsAuthenticated]


# =======================================
# ViewSet pour Depense
# =======================================
class DepenseViewSet(viewsets.ModelViewSet):
    queryset = Depense.objects.all().order_by('-date_creation')
    serializer_class = DepenseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def marquer_payee(self, request, pk=None):
        depense = self.get_object()
        try:
            depense.marquer_payee()
            serializer = self.get_serializer(depense)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        depense = self.get_object()
        try:
            depense.annuler()
            serializer = self.get_serializer(depense)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =======================================
# ViewSet pour BulletinPaie
# =======================================
class BulletinPaieViewSet(viewsets.ModelViewSet):
    queryset = BulletinPaie.objects.all().order_by('-annee', '-mois')
    serializer_class = BulletinPaieSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        bulletin = self.get_object()
        try:
            bulletin.valider()
            serializer = self.get_serializer(bulletin)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =======================================
# ViewSet pour ValidationDemande
# =======================================
class ValidationDemandeViewSet(viewsets.ModelViewSet):
    queryset = ValidationDemande.objects.all().order_by('-date_reception')
    serializer_class = ValidationDemandeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approuver(self, request, pk=None):
        instance = self.get_object()
        responsable_finance_id = request.data.get('responsable_finance_id')
        commentaire = request.data.get('commentaire', '')

        if not responsable_finance_id:
            return Response({'error': 'responsable_finance_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance.approuver(responsable_finance_id=UUID(responsable_finance_id), commentaire=commentaire)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def rejeter(self, request, pk=None):
        instance = self.get_object()
        responsable_finance_id = request.data.get('responsable_finance_id')
        commentaire = request.data.get('commentaire', '')

        if not responsable_finance_id:
            return Response({'error': 'responsable_finance_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance.rejeter(responsable_finance_id=UUID(responsable_finance_id), commentaire=commentaire)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def envoyer_decaissement(self, request, pk=None):
        """Crée une demande de décaissement depuis cette ValidationDemande"""
        instance = self.get_object()
        responsable_finance_id = request.data.get('responsable_finance_id')

        if not responsable_finance_id:
            return Response({'error': 'responsable_finance_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decaissement = instance.creer_demande_decaissement(responsable_finance_id=UUID(responsable_finance_id))
            serializer = DemandeDecaissementSerializer(decaissement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =======================================
# ViewSet pour DemandeDecaissement
# =======================================
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all().order_by('-date_demande')
    serializer_class = DemandeDecaissementSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approuver(self, request, pk=None):
        instance = self.get_object()
        coordinateur_id = request.data.get('coordinateur_id')
        commentaire = request.data.get('commentaire', '')

        if not coordinateur_id:
            return Response({'error': 'coordinateur_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance.approuver(coordinateur_id=UUID(coordinateur_id), commentaire=commentaire)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def rejeter(self, request, pk=None):
        instance = self.get_object()
        coordinateur_id = request.data.get('coordinateur_id')
        commentaire = request.data.get('commentaire', '')

        if not coordinateur_id:
            return Response({'error': 'coordinateur_id requis'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance.rejeter(coordinateur_id=UUID(coordinateur_id), commentaire=commentaire)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
