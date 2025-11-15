from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    District, Commune, Fokontany, Fonction, Affectation,
    Employer, TypeConge, Conge, TypeContrat, Contrat, Location,
    Electricite, ModePayement, Demande, Payement,
    TypeAchat, Achat
)
from .serializers import (
    DistrictSerializer, CommuneSerializer, FokontanySerializer,
    FonctionSerializer, AffectationSerializer, EmployerSerializer,TypeCongeSerializer, 
    CongeSerializer, TypeContratSerializer, ContratSerializer,
    LocationSerializer, ElectriciteSerializer, ModePayementSerializer, DemandeSerializer, PayementSerializer,
    TypeAchatSerializer, AchatSerializer
)


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all().order_by('name')
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'region']
    ordering_fields = ['name', 'region', 'created_at']


class CommuneViewSet(viewsets.ModelViewSet):
    queryset = Commune.objects.select_related('district').all()
    serializer_class = CommuneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['district']
    search_fields = ['name', 'code', 'district__name']
    ordering_fields = ['name', 'created_at']


class FokontanyViewSet(viewsets.ModelViewSet):
    queryset = Fokontany.objects.select_related('commune', 'commune__district').all()
    serializer_class = FokontanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['commune']
    search_fields = ['name', 'code', 'commune__name']
    ordering_fields = ['name', 'created_at']


class FonctionViewSet(viewsets.ModelViewSet):
    queryset = Fonction.objects.all()
    serializer_class = FonctionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom_fonction', 'description']
    ordering_fields = ['nom_fonction', 'created_at']





class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.select_related('fonction', 'district').all()
    serializer_class = EmployerSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status_employer', 'fonction', 'district', 'diplome']
    search_fields = ['nom_employer', 'prenom_employer', 'email', 'domaine_etude']
    ordering_fields = ['nom_employer', 'date_entree', 'created_at']

    @action(detail=False, methods=['get'])
    def actifs(self, request):
        queryset = self.queryset.filter(status_employer='actif')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        employer = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Employer.STATUS_CHOICES):
            return Response({'error': 'Status invalide'}, status=status.HTTP_400_BAD_REQUEST)
        employer.status_employer = new_status
        employer.save()
        serializer = self.get_serializer(employer)
        return Response(serializer.data)

class AffectationViewSet(viewsets.ModelViewSet):
    queryset = Affectation.objects.select_related(
        'nouveau_fonction', 'nouveau_district',
        'ancienne_fonction', 'ancien_district',
        'employer'
    ).all()
    serializer_class = AffectationSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'status_affectation',
        'type_affectation',
        'nouveau_fonction',
        'nouveau_district',
        'employer',
        'employer__id',
    ]
    search_fields = [
        'nouveau_fonction__nom_fonction',
        'nouveau_district__name',
        'employer__nom_employer',
        'employer__id',
    ]
    ordering_fields = ['date_creation_affectation', 'date_fin']

    @action(detail=False, methods=['get'])
    def active(self, request):
        affectations = self.filter_queryset(self.get_queryset()).filter(status_affectation='active')
        serializer = self.get_serializer(affectations, many=True)
        return Response(serializer.data)

class TypeCongeViewSet(viewsets.ModelViewSet):
    queryset = TypeConge.objects.all()
    serializer_class = TypeCongeSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']


# ----------------------------
# ViewSet Conge
# ----------------------------

class CongeViewSet(viewsets.ModelViewSet):
    queryset = Conge.objects.all().order_by('-date_creation')
    serializer_class = CongeSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        """
        Filtrer par employé si paramètre `employer_id` présent
        """
        queryset = super().get_queryset()
        employer_id = self.request.query_params.get('employer_id')
        if employer_id:
            queryset = queryset.filter(employer__id=employer_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Création d'un congé avec validation automatique
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conge = serializer.save()
        return Response(self.get_serializer(conge).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Mise à jour d'un congé
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        conge = serializer.save()
        return Response(self.get_serializer(conge).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Action pour approuver un congé
        """
        conge = self.get_object()
        conge.status_conge = 'approuve'
        conge.save()
        return Response({'status': 'Congé approuvé'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Action pour refuser un congé
        """
        conge = self.get_object()
        conge.status_conge = 'refuse'
        conge.save()
        return Response({'status': 'Congé refusé'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Action pour annuler un congé
        """
        conge = self.get_object()
        conge.status_conge = 'annule'
        conge.save()
        return Response({'status': 'Congé annulé'}, status=status.HTTP_200_OK)



class TypeContratViewSet(viewsets.ModelViewSet):
    queryset = TypeContrat.objects.all()
    serializer_class = TypeContratSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom_type', 'description']
    ordering_fields = ['nom_type', 'created_at']

class ContratViewSet(viewsets.ModelViewSet):
    queryset = Contrat.objects.select_related('type_contrat', 'employer').all()
    serializer_class = ContratSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status_contrat', 'type_contrat', 'employer']
    search_fields = ['employer__nom_employer', 'employer__prenom_employer']
    ordering_fields = ['date_debut_contrat', 'date_fin_contrat', 'salaire']

    @action(detail=False, methods=['get'])
    def actifs(self, request):
        contrats = self.queryset.filter(status_contrat='actif')
        serializer = self.get_serializer(contrats, many=True)
        return Response(serializer.data)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.select_related('affectation').all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ville', 'affectation']
    search_fields = ['adresse', 'ville', 'code_postal']
    ordering_fields = ['ville', 'created_at']


class ElectriciteViewSet(viewsets.ModelViewSet):
    queryset = Electricite.objects.select_related('location').all()
    serializer_class = ElectriciteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'fournisseur']
    search_fields = ['numero_compteur', 'fournisseur']
    ordering_fields = ['numero_compteur', 'created_at']



class ModePayementViewSet(viewsets.ModelViewSet):
    queryset = ModePayement.objects.all()
    serializer_class = ModePayementSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['mode_payement', 'description']
    ordering_fields = ['mode_payement', 'created_at']


class DemandeViewSet(viewsets.ModelViewSet):
    queryset = Demande.objects.select_related('employer').all()
    serializer_class = DemandeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'employer']
    search_fields = ['description', 'employer__nom_employer', 'employer__prenom_employer']
    ordering_fields = ['date_demande', 'montant']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        demande = self.get_object()
        demande.status = 'approuve'
        demande.save()
        serializer = self.get_serializer(demande)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        demande = self.get_object()
        demande.status = 'refuse'
        demande.save()
        serializer = self.get_serializer(demande)
        return Response(serializer.data)


class PayementViewSet(viewsets.ModelViewSet):
    queryset = Payement.objects.select_related(
        'mode_payement', 'demande', 'electricite', 'loyer'
    ).all()
    serializer_class = PayementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'mode_payement', 'demande', 'electricite']
    search_fields = ['reference']
    ordering_fields = ['date_payement', 'montant']

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        payement = self.get_object()
        payement.status = 'complete'
        payement.save()
        serializer = self.get_serializer(payement)
        return Response(serializer.data)


class TypeAchatViewSet(viewsets.ModelViewSet):
    queryset = TypeAchat.objects.all()
    serializer_class = TypeAchatSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['type_achat', 'nom', 'description']
    ordering_fields = ['nom', 'created_at']


class AchatViewSet(viewsets.ModelViewSet):
    queryset = Achat.objects.select_related('type_achat').all()
    serializer_class = AchatSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_achat', 'date_achat']
    search_fields = ['article', 'code_achat']
    ordering_fields = ['date_achat', 'montant', 'created_at']

    @action(detail=False, methods=['get'])
    def recent(self, request):
        achats = self.queryset.order_by('-date_achat')[:10]
        serializer = self.get_serializer(achats, many=True)
        return Response(serializer.data)
