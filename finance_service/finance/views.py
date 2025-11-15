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
# ViewSet TypeDecaissement
# =======================================
class TypeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = TypeDecaissement.objects.all()
    serializer_class = TypeDecaissementSerializer
    permission_classes = [IsAuthenticated]


# =======================================
# ViewSet DemandeDecaissement
# =======================================
class DemandeDecaissementViewSet(viewsets.ModelViewSet):
    queryset = DemandeDecaissement.objects.all().order_by('-date_demande')
    serializer_class = DemandeDecaissementSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approuver(self, request, pk=None):
        demande = self.get_object()
        coordinateur_id = request.data.get('coordinateur_id')
        commentaire = request.data.get('commentaire', '')
        try:
            demande.approuver(coordinateur_id=coordinateur_id, commentaire=commentaire)
            serializer = self.get_serializer(demande)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def rejeter(self, request, pk=None):
        demande = self.get_object()
        coordinateur_id = request.data.get('coordinateur_id')
        commentaire = request.data.get('commentaire', '')
        try:
            demande.rejeter(coordinateur_id=coordinateur_id, commentaire=commentaire)
            serializer = self.get_serializer(demande)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =======================================
# ViewSet Depense
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
# ViewSet BulletinPaie
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
# ViewSet ValidationDemande
# =======================================
class ValidationDemandeViewSet(viewsets.ModelViewSet):
    queryset = ValidationDemande.objects.all().order_by('-date_reception')
    serializer_class = ValidationDemandeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def approuver(self, request, pk=None):
        validation = self.get_object()
        responsable_finance_id = request.data.get('responsable_finance_id')
        commentaire = request.data.get('commentaire', '')
        try:
            validation.approuver(responsable_finance_id=responsable_finance_id, commentaire=commentaire)
            serializer = self.get_serializer(validation)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def rejeter(self, request, pk=None):
        validation = self.get_object()
        responsable_finance_id = request.data.get('responsable_finance_id')
        commentaire = request.data.get('commentaire', '')
        try:
            validation.rejeter(responsable_finance_id=responsable_finance_id, commentaire=commentaire)
            serializer = self.get_serializer(validation)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
