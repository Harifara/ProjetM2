from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.authentication import BasicAuthentication

from .authentication import KongJWTAuthentication
from .models import (
    District, Commune, Fokontany,
    Department, Function, Contract,
    Employee, Assignment, CV,
    LeaveType, LeaveRequest,
    Payslip, PaymentRequest
)
from .serializers import (
    DistrictSerializer, CommuneSerializer, FokontanySerializer,
    DepartmentSerializer, FunctionSerializer, ContractSerializer,
    EmployeeSerializer, AssignmentSerializer, CVSerializer,
    LeaveTypeSerializer, LeaveRequestSerializer,
    PayslipSerializer, PaymentRequestSerializer
)

# ==================== MIXIN AUTH ====================

class DefaultAuthMixin:
    """Mixin pour utiliser KongJWTAuthentication et permissions globales"""
    authentication_classes = [KongJWTAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_kong_user_id(self):
        """Retourne l'id de l'utilisateur Kong ou None"""
        return getattr(self.request.user, "id", None)


# ==================== GEOGRAPHIE ====================

class DistrictViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = District.objects.all().order_by('name')
    serializer_class = DistrictSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'region']


class CommuneViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Commune.objects.select_related('district').all()
    serializer_class = CommuneSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'district__name']


class FokontanyViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Fokontany.objects.select_related('commune', 'commune__district').all()
    serializer_class = FokontanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'commune__name']


# ==================== RESSOURCES HUMAINES ====================

class DepartmentViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer


class FunctionViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Function.objects.all().order_by('name')
    serializer_class = FunctionSerializer


class ContractViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Contract.objects.all().order_by('-start_date')
    serializer_class = ContractSerializer


class EmployeeViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        'department', 'function', 'contract',
        'fokontany', 'commune', 'district'
    ).all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'employee_number', 'email']

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.get_kong_user_id())


# ==================== AFFECTATIONS ====================

class AssignmentViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('employee').all()
    serializer_class = AssignmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['employee__first_name', 'employee__last_name']

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.get_kong_user_id())


# ==================== CV ====================

class CVViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = CV.objects.select_related('employee').all()
    serializer_class = CVSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by_id=self.get_kong_user_id())

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        cv = self.get_object()
        cv.status = 'approved'
        cv.validated_by_id = self.get_kong_user_id()
        cv.validated_at = timezone.now()
        cv.save()
        return Response({'status': 'CV approuvé'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        cv = self.get_object()
        cv.status = 'rejected'
        cv.validation_notes = request.data.get('notes', '')
        cv.validated_by_id = self.get_kong_user_id()
        cv.validated_at = timezone.now()
        cv.save()
        return Response({'status': 'CV rejeté'}, status=status.HTTP_200_OK)


# ==================== CONGÉS ====================

class LeaveTypeViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer


class LeaveRequestViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee', 'leave_type').all()
    serializer_class = LeaveRequestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['employee__first_name', 'employee__last_name', 'status']

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.get_kong_user_id())

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.approved_by_id = self.get_kong_user_id()
        leave.approved_at = timezone.now()
        leave.save()
        return Response({'status': 'Demande approuvée'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'rejected'
        leave.rejection_reason = request.data.get('reason', '')
        leave.approved_by_id = self.get_kong_user_id()
        leave.approved_at = timezone.now()
        leave.save()
        return Response({'status': 'Demande rejetée'}, status=status.HTTP_200_OK)


# ==================== BULLETINS DE PAIE ====================

class PayslipViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = Payslip.objects.select_related('employee').all()
    serializer_class = PayslipSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['employee__first_name', 'employee__last_name', 'year', 'month']

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.get_kong_user_id())

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        payslip = self.get_object()
        payslip.status = 'validated'
        payslip.validated_by_id = self.get_kong_user_id()
        payslip.validated_at = timezone.now()
        payslip.save()
        return Response({'status': 'Bulletin validé'}, status=status.HTTP_200_OK)


# ==================== DEMANDES DE PAIEMENT ====================

class PaymentRequestViewSet(DefaultAuthMixin, viewsets.ModelViewSet):
    queryset = PaymentRequest.objects.select_related('employee').all()
    serializer_class = PaymentRequestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['payment_type', 'status', 'employee__first_name']

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.get_kong_user_id())

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'approved'
        payment.approved_by_id = self.get_kong_user_id()
        payment.approved_at = timezone.now()
        payment.save()
        return Response({'status': 'Paiement approuvé'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'rejected'
        payment.review_notes = request.data.get('notes', '')
        payment.reviewed_by_id = self.get_kong_user_id()
        payment.reviewed_at = timezone.now()
        payment.save()
        return Response({'status': 'Paiement rejeté'}, status=status.HTTP_200_OK)
